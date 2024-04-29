from fastapi import APIRouter, Depends, Body, HTTPException
from fastapi.responses import JSONResponse
from starlette import status
from models.courier_users import *
from models.orders_model import *
from sqlalchemy.orm import sessionmaker, Session
from db import engine_s, SessionLocal
from typing import Union, Annotated
from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


users_router = APIRouter(tags = ["courier"])

@users_router.get("/api/courier", response_model=Union[list[Main_User_2]])
async def get_courier_db(DB: AsyncSession = Depends(get_session)):
    '''Получение информации о всех курьерах системе.'''
    users = await DB.execute(select(User))
    users = users.scalars().all()
    if users == None:
        return JSONResponse(status_code=404, content={"message": "Пользователи не найдены"})
    else:
        return users

@users_router.post("/api/courier", response_model=Union[Main_User_3], status_code=status.HTTP_201_CREATED)
async def create_courier(item: Annotated[Main_User_3, Body(embell=True, description="Новый пользователь")], DB: AsyncSession = Depends(get_session)):
    '''Регистрация курьера в системе.'''
    try:
        user = User(name=item.name, district=item.district)
        if user is None:
            raise HTTPException(status_code=404, detail="Объект не определен")
        DB.add(user)
        await DB.commit()
        await DB.refresh(user)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла ошибка при добавлении объекта")

@users_router.get("/api/courier/{id}", response_model=Union[Main_User_5])
async def get_courier_(id: int, DB: AsyncSession = Depends(get_session)):
    """Получение подробной информации о курьере."""
    user = await DB.execute(select(User).filter(User.id_user == id))
    user = user.scalars().first()
    if user == None:
        return JSONResponse(status_code=484, content={"message": "Пользователь не найден"})
    else:
        return user


@users_router.put('/api/courier', response_model=Union[Main_User_2, None])
async def edit_courier_something(item: Annotated[Main_User_2, Body(embed=True, description="Изменяем данные курьера по id")], DB: AsyncSession = Depends(get_session)):
    '''Изменение данных о курьере (всех)'''
    user = await DB.execute(select(User).where(User.id_user == item.id_user))
    user = user.scalars().first()
    if user == None:
        return JSONResponse(status_code=404, content={"message":"Пользователь не найден"})
    user.name = item.name
    user.district = item.district
    try:
        await DB.commit()
        await DB.refresh(user)
    except HTTPException:
        return JSONResponse(status_code=404, content={"message":"Ошибка"})
    return user


@users_router.patch('/{id}', response_model=Union[Main_User_5, None])
async def edit_courier(item: Annotated[Main_User_5, Body(embed=True, description="Изменяем данные страны по id")], DB: AsyncSession = Depends(get_session)):
    '''Изменение данных о курьере (частично)'''
    try:
        user = await DB.execute(select(User).where(User.id_user == item.id_user))
        user = user.scalars().first()
        if user == None:
            return JSONResponse(status_code=404, content={"message":"Пользователь не найден"})
        if "string" != item.name:
            user.name = item.name
        if ["string"] != item.district:
            user.district = item.district
        if {} != item.active_order:
            user.active_order = item.active_order
        try:
            await DB.commit()
            await DB.refresh(user)
        except HTTPException:
            return JSONResponse(status_code=404, content={"message":"Ошибка"})
        return user
    except HTTPException:
        return JSONResponse(status_code=404, content={"message":"Ошибка"})

@users_router.delete('/api/courier{id}', response_model=Union[list[Main_User_1], None])
async def delete_courier(id: int, DB: AsyncSession = Depends(get_session)):
    '''Удалить курьера из системы'''
    user = await DB.execute(select(User).where(User.id_user == id))
    user = user.scalars().first()
    if user == None:
        return JSONResponse(status_code=404, content={"message": "Пользователь не найден"})
    try:
        await DB.delete(user)
        await DB.commit()
    except HTTPException:
        return JSONResponse(status_code=404, content={"message": "Ошибка"})
    return JSONResponse(content={"message": f"Пользователь {id} удален"})



