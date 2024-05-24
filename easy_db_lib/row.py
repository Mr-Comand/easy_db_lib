from typing import Iterable
from .database import Database

class Row(object):
    def __init__(self, db: Database, tableName, identifierKeys = None, toBeCreated:bool = False, fields:dict = {}, autoPull=False, **values) -> None:
        self.fields = fields
        self.db = db
        self.toBeCreated = toBeCreated
        self.autoPull = autoPull
        if toBeCreated:
            self.changes = set()
        self.tableName = tableName
        self.identifierKeys = identifierKeys
        self.links = set()
        self._linkNames = list()
        for field in self.fields.keys():
            # TODO Values
            setattr(self, "_"+field, values[field] if field in values else None)
            if "references" in self.fields[field] and self.fields[field]["references"]:
                self.links.add(field)
                self._linkNames.append(field+"_link")
                
    def __setattr__(self, name: str, value: object) -> None:
        if name == "fields":
            object.__setattr__(self, name, value)
            return
        try:
            if name.endswith("_link"):
                field = name[0:-5]
                if field in self.links:
                    if isinstance(value, self.fields[field]["references"]["table"].table_element):
                        if self.toBeCreated:
                            object.__setattr__(self, "_"+name+"_", value)
                            object.__setattr__(self, "_"+field, getattr(value, self.fields[field]["references"]["column"]))
                            self.changes.add(field)
                        else:
                            if value.toBeCreated:
                                value.create()
                            object.__setattr__(self, "_"+field, getattr(value, self.fields[field]["references"]["column"]))
                            self.push([field])
                    else:
                        raise TypeError(f"{value} is not a row of {self.fields[field]["references"]["table"]}.")
            if name in self.fields:
                print("set", name)
                setattr(self, '_' + name, value)
                if not self.toBeCreated:
                    self.push([name])
                else:
                    self.changes.add(name)
        except AttributeError:
            None
        else:
            object.__setattr__(self, name, value)
    
    def __getattribute__(self, name: str) -> object:
        if name == "fields":
            return object.__getattribute__(self, name)
        try:
            if name.endswith("_link"):
                if hasattr(self, "_"+name+"_"):
                    return object.__getattribute__(self, "_"+name+"_")
                else:
                    if name in self._linkNames:
                        field = name[0:-5]
                        element = self.fields[field]["references"]["table"].table_element(autoPull=self.autoPull, **{self.fields[field]["references"]["column"]:getattr(self, field)})
                        setattr(self, "_"+name+"_", element)
                        return element
            if name in self.fields:
                if self.autoPull or not hasattr(self, '_' + name):
                    print("pull",name)
                    self.pull([name])
                print("ret",name)
                return getattr(self, '_' + name)

        except AttributeError:
            None
        else:
            return object.__getattribute__(self, name)
    def __dir__(self) -> Iterable[str]: 
        return list(self.fields.keys()) + list(object.__dir__(self)) + self._linkNames
    def pull(self, fields: list = None) -> None:
        if self.toBeCreated:
            print(fields)
            return None
        if fields is None:
            fields = self.fields.keys()
        selected_fields = ', '.join(fields)
        identifier = " AND ".join([f"{field}='{getattr(self, '_' + field)}'" for field in self.identifierKeys])
        print(identifier)
        result = self.db.execute(f"SELECT {selected_fields} FROM {self.tableName} WHERE {identifier}")
        if result:
            for index, field in enumerate(fields):
                if result[0][index] and isinstance(self.fields[field]["type"], dict):
                    setattr(self, '_' + field, self.fields[field]["type"]["python"].__call__(result[0][index]))
                else:
                    setattr(self, '_' + field, result[0][index])
        else:
            raise ValueError(f"No Element found with {identifier} in {self.tableName}")

    def push(self, fields: list = None) -> None:
        if fields is None:
            fields = self.fields.keys()
        updated_fields = ', '.join([f"{field}='{getattr(self, '_' + field)}'" for field in fields])
        identifier = " AND ".join([f"{field}='{getattr(self, '_' + field)}'" for field in self.identifierKeys])
        self.db.execute(f"UPDATE {self.tableName} SET {updated_fields} WHERE {identifier}")
    def create(self) -> None:
        if self.toBeCreated:
            fields = self.changes
            changed_links = list(set(fields).intersection(self.links))
            for field in changed_links:
                value = getattr(self, "_"+field+"_link_")
                object.__setattr__(self, "_"+field, getattr(value, self.fields[field]["references"]["column"]))
                if value.toBeCreated:
                    value.create()
            fields_str = ', '.join(fields)
            values = ', '.join(["%s" for _ in fields])
            
            query = f"INSERT INTO {self.tableName} ({fields_str}) VALUES ({values})"
            missingIdentifierKeys = [key for key in self.identifierKeys if key not in fields]
            if len(missingIdentifierKeys)!=0:
                query += f" RETURNING { ', '.join(missingIdentifierKeys)}"
            params = [getattr(self, field) for field in fields]
            print(query, params, missingIdentifierKeys)
            
            output = self.db.execute(query, params)
            if len(missingIdentifierKeys)!=0:
                for i, key in enumerate(missingIdentifierKeys):
                    print(output)
                    setattr(self, key, output[0][i])
            
            self.toBeCreated = False
            del(self.changes)
            
        else:
            raise TypeError("The Object was not initialized to be created.")
        
    def delete(self) -> None:
        identifier = " AND ".join([f"{field}='{getattr(self, '_' + field)}'" for field in self.identifierKeys])
        self.db.execute(f"DELETE FROM {self.tableName} WHERE {identifier};")

    def __str__(self) -> str:
        values = ""
        for field in self.fields.keys():
            suffix = ""
            if field in self.identifierKeys:
                suffix += "[PK]"
            if ("references" in self.fields[field]) and self.fields[field]["references"]:
                suffix += "[REF]"
            if self.autoPull:
                values += f"{field}{suffix}={getattr(self, field)}, "
            else:
                values += f"{field}{suffix}={getattr(self, '_' + field)}, "
        # Remove trailing comma and space
        values = values.rstrip(", ")
        
        return f"Table_Element(db={self.db}, table_name={self.tableName}, toBeCreated={self.toBeCreated}, autoPull={self.autoPull}, {values})"
