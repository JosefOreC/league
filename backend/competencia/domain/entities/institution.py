from .institution_category import InstitutionCategory

class Institution:
    def __init__(self, id:int, name:str, category:InstitutionCategory, city:str, code:str):
        self.__id = id
        self.__name = name
        self.__category = category
        self.__city = city
        self.__code = code
    
    @property
    def id(self) -> int:
        return self.__id
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def category(self) -> InstitutionCategory:
        return self.__category
    
    @property
    def city(self) -> str:
        return self.__city
    
    @property
    def code(self) -> str:
        return self.__code
    
    @id.setter
    def id(self, id: int):
        if not isinstance(id, int) or not id:
            raise ValueError("El id debe ser un entero no vacío")
        self.__id = id
    
    @name.setter
    def name(self, name: str):
        if not isinstance(name, str) or not name:
            raise ValueError("El nombre debe ser una cadena no vacía")
        self.__name = name
    
    @category.setter
    def category(self, category: InstitutionCategory):
        if not isinstance(category, InstitutionCategory):
            raise ValueError("La categoría debe ser una categoría")
        self.__category = category
    
    @city.setter
    def city(self, city: str):
        if not isinstance(city, str) or not city:
            raise ValueError("La ciudad debe ser una cadena no vacía")
        self.__city = city
    
    @code.setter
    def code(self, code: str):
        if not isinstance(code, str) or not code:
            raise ValueError("El código debe ser una cadena no vacía")
        self.__code = code
        