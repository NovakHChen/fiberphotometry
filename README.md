# Fiberphotometry
Basic routines for reading, visualizing and analyzing fiberphotometry recordings 

## Local Installation:

1. install Anaconda
1. Create a new environment by running the following lines in the anaconda terminal

    ```bash
    conda create --name fiberphotometry python=3.9
    ```
1. activte the environment:
    ```bash
    conda activate fiberphotometry
    ```
1. clone the repository:
    ```bash 
    git clone https://github.com/GergelyTuri/fiberphotometry.git
    ```
1. change directories
    ```bash
    cd fiberphotometry
    ```
1. finally:
    ```bash 
    pip install .
    ```

## Installation in a Google Colab notebook

1. open a Colab notebook then type this in a code cell:
    ```bash    
    !git clone https://github.com/GergelyTuri/fiberphotometry.git
    %cd fiberphotometry
    !pip install .
    ```
1. you may need to restart your runtime/session after this. 
1. you can mount your cloud drive in the notebook so you have access to your data. E.g.:
    ```bash
    from google.colab import drive
    drive.mount('/gdrive')
    ```

## Requirements
The only requirement at this point is the Tucker Davis fiber photometry library which can be installed trough pip:
`pip install tdt`