import sys
from pyH2A.run_pyH2A import pyH2A
from tests.test_pec import test_pec
from tests.test_photocatalytic import test_photocatalytic
from tests.test_pve import test_pve

def update_all():
    test_pve()
    pyH2A('./tests/PV_E.md', './tests/Results/PV_E/', snapshot_directory="tests/snapshots/PV_E/")
    
    test_pec()
    pyH2A('./tests/PEC.md', './tests/Results/PEC/', snapshot_directory="tests/snapshots/PEC/")
    
    test_photocatalytic()
    pyH2A('./tests/Photocatalytic.md', './tests/Results/Photocatalytic/', snapshot_directory="tests/snapshots/Photocatalytic/")

def main():
    if len(sys.argv) < 2:
        choice = input("Update all snapshots or specify (pve, pec, photocatalytic)? [all/pve/pec/photocatalytic]: ").strip().lower()
    else:
        choice = sys.argv[1].strip().lower()
    
    if choice == "all":
        update_all()
    elif choice == "pve":
        test_pve()
        pyH2A('./tests/PV_E.md', './tests/Results/PV_E/', snapshot_directory="tests/snapshots/PV_E/")
    elif choice == "pec":
        test_pec()
        pyH2A('./tests/PEC.md', './tests/Results/PEC/', snapshot_directory="tests/snapshots/PEC/")
    elif choice == "photocatalytic":
        test_photocatalytic()
        pyH2A('./tests/Photocatalytic.md', './tests/Results/Photocatalytic/', snapshot_directory="tests/snapshots/Photocatalytic/")
    else:
        print("Invalid choice. Please use 'all', 'pve', 'pec', or 'photocatalytic'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
