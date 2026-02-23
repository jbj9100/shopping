from pydantic import BaseModel, ConfigDict

# snake_case -> camelCase로 변경할경우
# def to_camel(s: str) -> str:
#     parts = s.split("_")
#     return parts[0] + "".join(p.title() for p in parts[1:])
# camelCase - {"id": 1, "originalPrice": 2000, "freeShipping": True} 
# snake_case - {"id": 1, "original_price": 2000, "free_shipping": True} 

class APIModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True        
    )

# from_attributes=True 하면
# ✅ 가능해짐:
# UserOut.model_validate(user_orm)

# ❌ 원래는(옵션 없으면) 보통 이렇게 해야 했음 (dict 같은 매핑 데이터를 기대함)
# UserOut.model_validate({"id": user_orm.id, "username": user_orm.username, ...})
