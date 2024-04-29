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

orders_router = APIRouter(tags = ["order"])

@orders_router.get("/api/order", response_model=Union[list[Main_Order_5]])
async def get_all_orders_db(DB: AsyncSession = Depends(get_session)):
    '''Получение информации о всех заказах системе.'''
    orders = await DB.execute(select(Order))
    orders = orders.scalars().all()
    if orders == None:
        return JSONResponse(status_code=404, content={"message": "Пользователи не найдены"})
    else:
        return orders

@orders_router.post("/api/order", response_model=Union[Main_Order_2, Main_User_5], status_code=status.HTTP_201_CREATED)
async def create_order(name: str, district: str, DB: AsyncSession = Depends(get_session)):
    '''Публикация заказа в системе с полями:'''
    try:
        count = 0
        user_id = await DB.execute(select(User.id_user))
        user_id = user_id.scalars().all()
        order = Order(name=name, district=district)
        z = await DB.execute(select(User.district))
        z = z.scalars().all()
        for i in z:
            if district in i[0]:
                break
            count += 1
        order.id_user = user_id[count]
        order.status = 1
        if order is None:
            raise HTTPException(status_code=404, detail="Объект не определен")
        user = await DB.execute(select(User).where(User.id_user == user_id[count]).where(User.active_order == {}))
        user = user.scalars().first()
        if user is None:
            raise HTTPException(status_code=404, detail="Нет свободного курьера")
        DB.add(order)
        await DB.commit()
        await DB.refresh(order)
        user.active_order = {"order_id": order.id_order, "order_name": order.name}
        DB.add(user)
        await DB.commit()
        await DB.refresh(user)
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла ошибка при добавлении объекта. Нет подходящего курьера в данном районе")

@orders_router.get("/api/order/{id}", response_model=Union[Main_Order_3])
async def get_order(id: int, DB: AsyncSession = Depends(get_session)):
    """Получение информации о заказе."""
    order = await DB.execute(select(Order).where(Order.id_order == id))
    order = order.scalars().first()
    if order == None:
        return JSONResponse(status_code=484, content={"message": "Заказ не найден"})
    else:
        return order


@orders_router.post("/api/order{id}", response_model=Union[Main_Order_3, Main_User_5], status_code=status.HTTP_201_CREATED)
async def end_order(id: int, DB: AsyncSession = Depends(get_session)):
    '''Завершить заказ.'''
    order = await DB.execute(select(Order).where(Order.id_order == id))
    order = order.scalars().first()
    if order == None:
        return JSONResponse(status_code=484, content={"message": "Заказ не найден"})
    else:
        if order.status == 2:
            return JSONResponse(status_code=484, content={"message": "Заказ уже завершён"})

        user = await DB.execute(select(User).where(User.active_order == {"order_id": order.id_order, "order_name": order.name}))
        user = user.scalars().first()
        user.active_order = {}
        order.status = 2

        await DB.commit()
        await DB.refresh(order)

        await DB.commit()
        await DB.refresh(user)
        return order


@orders_router.delete('/api/order{id}', response_model=Union[Main_Order_4, Main_User_5])
async def delete_order(id: int, DB: AsyncSession = Depends(get_session)):
    try:
        order = await DB.execute(select(Order).where(Order.id_order == id))
        order = order.scalars().first()
        if order == None:
            return JSONResponse(status_code=404, content={"message": "Заказ не найден"})
        try:
            user = await DB.execute(select(User).where(User.active_order == {"order_id": order.id_order, "order_name": order.name}))
            user = user.scalars().first()
            user.active_order = {}
            await DB.commit()

        except:
            pass
        await DB.delete(order)
        await DB.commit()
        return JSONResponse(content={"message": f"Заказ {id} удален"})
    except HTTPException:
        return JSONResponse(status_code=404, content={"message": "Ошибка"})