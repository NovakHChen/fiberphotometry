import pandas as pd
import numpy as np
import os 
from src import behavior_dlc
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

def preprocess_dlc_data(file_path, exclude_columns=None, reset_index=True):
    """
    Preprocesses the DLC tracking data from an HDF file by renaming columns,
    excluding specific columns, and resetting the index if needed. But this 
    function will keep the shape of the dataframe but simply adding body parts 
    suffix to the columns.  

    Args:
        file_path (str): Path to the HDF file containing the DLC tracking data.
        exclude_columns (list): List of columns to exclude from the dataframe.
                                Default is ['tailbase_x', 'tailbase_y', 'tailbase_likelihood'].
        reset_index (bool): Whether to reset the index of the dataframe. Default is True.

    Returns:
        pd.DataFrame: Processed dataframe with renamed and filtered columns.
    """
    if exclude_columns is None:
        exclude_columns = ['tailbase_x', 'tailbase_y', 'tailbase_likelihood']

    # Read the HDF file
    data = pd.read_hdf(file_path)

    # Rename columns to remove the first part of the multi-index and join the remaining parts
    data.columns = ['_'.join(col[1:]).strip() for col in data.columns]

    # Exclude specified columns
    data = data.loc[:, ~data.columns.isin(exclude_columns)]

    # Reset the index if specified
    if reset_index:
        data = data.reset_index()

    return data


def dlc_to_long(file_path):
    """
    Transforms wide DLC data into a long format, using metadata rows to structure columns
    and extracts cohort_id from the file name.

    Parameters:
    - file_path: String representing the file path to the wide-format positional data CSV.

    Returns:
    - long_data: DataFrame in long format with columns ['x', 'y', 'likelihood', 'body_part', 'index', 'id', 'group'].
    """
    # Extract file name and metadata
    file_name = os.path.basename(file_path)
    parts = os.path.splitext(file_name)[0].split('_')

    # Load the data using the Behavior class
    beh = behavior_dlc.Behavior(file_path)
    df = beh.data

    # Define body parts and coordinates
    body_parts = ['nose', 'leftear', 'rightear', 'neck', 'back1', 'back2', 'tailbase']
    coordinates = ["x", "y", "likelihood"]

    # Generate column names
    column_names = [f"{body}_{coord}" for body in body_parts for coord in coordinates]

    # Assign column names to the DataFrame
    df.columns = column_names

    # Convert the DataFrame to long format
    long_data = pd.DataFrame()
    for part in body_parts:
        part_data = df[[f"{part}_x", f"{part}_y", f"{part}_likelihood"]].copy()
        part_data.columns = ['x', 'y', 'likelihood']
        part_data['body_part'] = part
        part_data['index'] = part_data.index
        part_data['id'] = parts[0]  # Extracted ID from the file name
        part_data['group'] = parts[1]  # Extracted group info from the file name
        long_data = pd.concat([long_data, part_data], ignore_index=True)

    return long_data


def process_dlc_folder(folder_path):
    """
    Processes all relevant DLC CSV files in a folder, converts them to long format, and
    concatenates them into a single DataFrame.

    Parameters:
    - folder_path: String representing the path to the folder containing DLC CSV files.

    Returns:
    - combined_data: DataFrame containing all processed data in long format.
    """
    combined_data = pd.DataFrame()

    # List all files in the folder
    all_files = os.listdir(folder_path)

    # Filter for relevant DLC CSV files
    dlc_files = [f for f in all_files if f.endswith('.h5')]

    successful_count = 0

    # Process each file
    for file_name in dlc_files:
        file_path = os.path.join(folder_path, file_name)
        # Process the file using dlc_to_long
        try:
            long_data = dlc_to_long(file_path)
            combined_data = pd.concat([combined_data, long_data], ignore_index=True)
            successful_count += 1
        except Exception as e:
            print(f"Error processing {file_name}: {e}")
            continue

    print(f"Successfully processed {successful_count} files.")

    return combined_data



def pairwise_dist(coords: pd.Series) -> pd.Series:
    """
    Computes consecutive pairwise differences in a Series.

    NOTE: This is a helper function for distance_moved.

    Args:
        coords (pd.Series): A one-dimensional pandas Series of coordinates over time.

    Returns:
        pd.Series: Series containing consecutive differences (coords[i] - coords[i-1]).
    """
    if coords.empty:
        raise ValueError("coords cannot be empty!")

    # Compute differences using pandas `.diff()`
    delta_coords = coords.astype(float).diff()

    return delta_coords


def distance_moved(data: pd.DataFrame, x_col: str, y_col: str) -> pd.Series:
    """
    Computes the distance moved per frame given x and y coordinates in a DataFrame.

    Args:
        data (pd.DataFrame): DataFrame containing at least two columns of coordinates (x and y).
        x_col (str): The name of the column containing x coordinates.
        y_col (str): The name of the column containing y coordinates.

    Returns:
        pd.Series: Series containing the distance moved per frame.
    """
    if x_col not in data.columns or y_col not in data.columns:
        raise KeyError(f"Columns '{x_col}' and/or '{y_col}' not found in the DataFrame!")

    if data[x_col].empty or data[y_col].empty:
        return pd.Series(np.nan, index=data.index)

    # Compute deltas for x and y coordinates
    delta_x = pairwise_dist(data[x_col])
    delta_y = pairwise_dist(data[y_col])

    # Compute Euclidean distance moved per frame
    dist_moved = np.sqrt(delta_x**2 + delta_y**2)

    return dist_moved


def compute_velocity(
    df: pd.DataFrame,
    dist_col: str = 'dist_moved',
    framerate: float = 10.0
) -> pd.Series:
    """
    Computes the velocity in pixels/second using the precomputed distance moved column,
    and sets velocity to 0 where distance moved is 0.

    Args:
        df (pd.DataFrame): The dataframe containing the distance moved column.
        dist_col (str): The name of the column containing the distance moved values. Default is 'dist_moved'.
        framerate (float): The frame rate of the video. Default is 10 fps.

    Returns:
        pd.Series: A pandas Series containing velocity in pixels/second.
    """
    if dist_col not in df.columns:
        raise KeyError(f"Column '{dist_col}' not found in the dataframe!")

    if framerate <= 0:
        raise ValueError("Framerate must be greater than 0.")

    # Calculate the time per frame
    time_per_frame = 1 / framerate

    # Compute velocity
    velocity = df[dist_col] / time_per_frame

    # Ensure velocity is 0 where distance moved is 0
    velocity.loc[df[dist_col] == 0] = 0

    return velocity


def apply_pca_and_velocity(data: pd.DataFrame, exclude_suffix: str = 'likelihood', n_components: int = 2, framerate: float = 10.0) -> pd.DataFrame:
    """
    Applies PCA to numeric columns in the input DataFrame, calculates distance moved and velocity.

    Args:
        data (pd.DataFrame): Input DataFrame containing numeric tracking data.
        exclude_suffix (str): Suffix to exclude columns (e.g., 'likelihood'). Default is 'likelihood'.
        n_components (int): Number of principal components to compute. Default is 2.
        framerate (float): Frame rate of the video for velocity calculation. Default is 10 fps.

    Returns:
        pd.DataFrame: DataFrame with added PCA components, distance moved, and velocity.
    """
    # Step 1: Select numeric columns excluding those with the specified suffix
    numeric_columns = [col for col in data.columns if not col.endswith(exclude_suffix)]
    numeric_data = data[numeric_columns].select_dtypes(include=[np.number])

    if numeric_data.empty:
        raise ValueError("No numeric columns found to apply PCA.")

    if numeric_data.shape[1] < n_components:
        raise ValueError(f"Number of components ({n_components}) cannot exceed the number of numeric columns ({numeric_data.shape[1]}).")

    # Step 2: Standardize the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(numeric_data)

    # Step 3: Apply PCA
    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(scaled_data)

    # Step 4: Create DataFrame for PCA results and add to original DataFrame
    pca_df = pd.DataFrame(pca_result, columns=[f'PC{i+1}' for i in range(n_components)], index=data.index)
    for col in pca_df.columns:
        if col in data.columns:
            raise ValueError(f"Column '{col}' already exists in the DataFrame. Consider renaming PCA components.")
        data[col] = pca_df[col]

    # Optional: Print or log explained variance ratio
    print("Explained Variance Ratio:", pca.explained_variance_ratio_)

    # Step 5: Calculate distance moved using PCA components
    data['pca_dist'] = distance_moved(data, 'PC1', 'PC2')

    # Step 6: Calculate velocity
    data['pca_vel'] = compute_velocity(data, dist_col='pca_dist', framerate=framerate)

    return data