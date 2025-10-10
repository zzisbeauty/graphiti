from pydantic import BaseModel  
  
class Person(BaseModel):  
    """学习者或知识创作者,如作者、老师、同学等具体的人"""  
    pass  
  
class Concept(BaseModel):  
    """具体的概念、术语或知识点,如'并发'、'操作系统'、'机器学习'等"""  
    pass  
  
class Resource(BaseModel):  
    """学习资源,如书籍、视频、文档、网站等具体材料"""  
    pass  
  
ENTITY_TYPES: dict[str, type[BaseModel]] = {  
    'Person': Person,  
    'Concept': Concept,  
    'Resource': Resource,  
}