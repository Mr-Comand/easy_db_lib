from typing import Iterable
from database import Database
from row import Row
class Table:
    def __init__(self, db: Database, createIfNotExists:bool = False, structure:dict = {}, autoPull = False) -> None:
        self.db = db
        self.structure = structure
        self.createIfNotExists = createIfNotExists
        self.tableName = self.structure['name']
        self.columns = self.structure['columns']
        self.autoPull = autoPull
        self.primaryKeys = []
        for column_name, column_specification in self.columns.items():
            if "primary" in column_specification:
                if column_specification["primary"]:
                    self.primaryKeys.append(column_name)
        
        class Defined_Table_Element(Row):
            def __init__(self_, toBeCreated:bool = False, identifierKeys=self.primaryKeys, autoPull=self.autoPull, **values) -> None:
                super().__init__(db=db, tableName=self.tableName, identifierKeys=identifierKeys, toBeCreated=toBeCreated, fields=self.columns, autoPull=autoPull, **values)
        self.table_element = Defined_Table_Element
        if createIfNotExists:
            self.create()


    def delete(self, type: str = "RESTRICT") -> None:
        """ Deletes the Table
        Args:
            type (str, optional): The type of deletion. Can be "NORMAL", "CASCADE" or "RESTRICT". Defaults to "RESTRICT".
        """
        match type:
            case "NORMAL" | "":
                self.db.execute(f"DROP TABLE {self.tableName};")
            case "CASCADE":
                self.db.execute(f"DROP TABLE {self.tableName} CASCADE;")
            case "RESTRICT" | _:
                self.db.execute(f"DROP TABLE {self.tableName} RESTRICT;")
            
    def create(self) -> None:

        # Construct the SQL CREATE TABLE statement
        sql = f"CREATE TABLE IF NOT EXISTS {self.tableName} ("

        # Add columns
        for column_name, column_specification in self.columns.items():
            sql += f"{column_name} "
            # type
            if "type" in column_specification:
                type_ = column_specification["type"]
                if isinstance(type_, dict):
                    type_ =  type_["sql"]
                sql += f"{type_} "
            else:
                raise KeyError(f"No type specified for column: {column_name}.")
            
            # not_null
            if "not_null" in column_specification:
                if column_specification["not_null"]:
                    sql += "NOT NULL "
            # default
            if "default" in column_specification:
                default = column_specification["default"] if column_specification["default"] is not None else "null"
                sql += f"DEFAULT {default} "
            # unique
            if "unique" in column_specification:
                if column_specification["unique"]:
                    sql += "UNIQUE "
            # check
            if "check" in column_specification:
                check = column_specification["check"]
                if check is not None:
                    sql += f"CHECK {check} "
            # references
            if "references" in column_specification:
                references = column_specification["references"]
                if references:
                    sql += f"REFERENCES {references["table"].tableName}({references["column"]}) "
            # other
            if "other" in column_specification:
                other = column_specification["other"]
                if other:
                    sql += f"{other} "
            
            sql += ", "
        
        # primary key
        if self.primaryKeys is not []:
            sql += f"PRIMARY KEY ({", ".join(self.primaryKeys)})"
        # Remove trailing comma and space
        sql = sql.rstrip(", ")

        # Close the statement
        sql += ");"
        # Execute the SQL statement
        self.db.execute(sql)
    def __str__(self) -> str:
        return f"DB_Table(name={self.tableName}, db={self.db}, columns=[{', '.join(self.columns.keys())}], createIfNotExists={self.createIfNotExists})"
    # TODO formattedContent
    def formattedContent(self, rows=10):
        sql= f"SELECT * FROM {self.tableName};"
        print(self.db.execute(sql))

if __name__ == "__main__":
    db = Database()
    table = Row(db,toBeCreated=True,identifierKeys=["timestamp"],fields={"timestamp":{"type":{"sql":"Text","python": type}, "PRIMARY": False, "references": {"table":"table_name", "column":"column_name"}}})
    #table2 = Table_Element(db,toBeCreated=True,primaryKeys=["timestamp2"],fields={"timestamp2":{"type":{"sql":"Text","python": type}, "PRIMARY": False, "references": {"table":"table_name", "column":"column_name"}}})
    print(dir(table))
    print(table)