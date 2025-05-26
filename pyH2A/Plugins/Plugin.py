import csv
import os
import logging
from pyH2A.DiscountedCashFlow import DiscountedCashFlow
from pyH2A.Utilities.input_modification import insert, process_table

class Plugin:
    def __init__(
            self, 
            dcf: DiscountedCashFlow
            ) -> None:
        self.dcf: DiscountedCashFlow = dcf
        self.mod: str = self.__class__.__module__ + "." + self.__class__.__name__
        self.insert_queue: list[dict] = []

        self.logger = logging.getLogger(self.mod)
        self.logger.info(f"Starting {self.__class__.__name__}")

    def process_table(
            self, 
            table_keys: list[str]
            ) -> None:
        """Processes input table."""
        for table_key in table_keys:
            process_table(self.dcf.inp, table_key, "Value")

    def process_insert_queue(
            self
            ) -> None:
        """Inserts the calculated values into the DCF."""
        if self.dcf.snapshot_directory != None:
            self._store_snapshot()

        for entry in self.insert_queue:
            self._process_insert(entry)
            if self.dcf.print_info:
                self.logger.debug(
                    f"{entry.get('key')} > {entry.get('subkey')} > Value: {entry.get('value')}"
                )
        self.insert_queue.clear()

    def _process_insert(
            self, 
            entry: dict[str, str | float | int | list[float] | None]
            ) -> None:
        """Inserts the calculated values into the DCF."""
        key = entry.get("key")
        subkey = entry.get("subkey")
        value = entry.get("value")
        field = entry.get("field", "Value")
        mod = entry.get("mod", __name__)
        print_info = entry.get("print_info", self.dcf.print_info)
        add_processed = entry.get("add_processed", True)
        insert_path = entry.get("insert_path", True)

        insert(
            self.dcf,
            key,
            subkey,
            field,
            value,
            mod,
            print_info=print_info,
            add_processed=add_processed,
            insert_path=insert_path,
        )

    def _store_snapshot(
            self
            ) -> None:
        """Stores insert queue dict entry keys (key, subkey, field) to a CSV file if store_snapshots is True."""
        if self.dcf.snapshot_directory is None:
            return

        dict_entries_file = f"{self.dcf.snapshot_directory}/{self.__class__.__name__}/dict_entries.csv"
        os.makedirs(os.path.dirname(dict_entries_file), exist_ok=True)

        with open(dict_entries_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["key", "subkey", "field"])
            for entry in self.insert_queue:
                key = entry.get("key", "")
                subkey = entry.get("subkey", "")
                field = entry.get("field", "Value")
                writer.writerow([key, subkey, field])
        self.logger.info(f"Stored snapshot entries to {dict_entries_file}")