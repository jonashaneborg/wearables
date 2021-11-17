from EDA import *

def main():
    eda = EDA("Empatica/Data/EDA.csv")
    eda.detect_MOS(plotting=True)

if __name__ == "__main__":
    main()
