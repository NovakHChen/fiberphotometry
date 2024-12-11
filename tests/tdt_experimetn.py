"""test for TDT_experiment class"""

from src import TDT_experiment

TDT_EXPERIEMNT_PATH = "/mnt/DataDrive1/shaharia/Test_Data/nia_02_5HT_cxtA_day_1"


def main():
    experiment = TDT_experiment.TDTExperiment(exp_path=TDT_EXPERIEMNT_PATH)
    print(experiment.analysis_path)
    print(experiment.stores_listings)
    print(experiment.notes)
    print(experiment.experiment_start_stop())
    print(experiment.experiment_name)
    print(experiment.subject_name)


if __name__ == "__main__":
    main()
