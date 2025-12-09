from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from src.domain.entities import Payment, PaymentStatus
from src.ports.repositories import PaymentRepository

class MongoPaymentRepository(PaymentRepository):
    def __init__(self, client: AsyncIOMotorClient, db_name: str):
        self.client = client
        self.db: AsyncIOMotorDatabase = self.client[db_name]
        self.collection = self.db.payments

    async def create(self, payment: Payment) -> Payment:
        payment_dict = payment.model_dump()        
        payment_dict["_id"] = payment_dict.pop("id")
        
        await self.collection.insert_one(payment_dict)
        
        return payment
    
    async def get_all(self) -> list[Payment]:
        payments = []
        cursor = self.collection.find()
        
        async for document in cursor:
            document["id"] = str(document.pop("_id"))
            payments.append(Payment(**document))
            
        return payments

    async def get_by_id(self, payment_id: str) -> Optional[Payment]:
        document = await self.collection.find_one({"_id": payment_id})
        
        if document:
            document["id"] = document.pop("_id")
            return Payment(**document)
            
        return None

    async def get_by_external_id(self, external_id: str) -> Optional[Payment]:
        document = await self.collection.find_one({"external_payment_id": external_id})
        
        if document:
            document["id"] = document.pop("_id")
            return Payment(**document)
            
        return None

    async def update_status(self, payment_id: str, status: PaymentStatus, external_id: Optional[str] = None) -> Optional[Payment]:
        update_data = {"status": status}
        if external_id:
            update_data["external_payment_id"] = external_id
            
        await self.collection.update_one(
            {"_id": payment_id},
            {"$set": update_data}
        )
        
        return await self.get_by_id(payment_id)
    
    async def get_by_order_id(self, order_id: str) -> Optional[Payment]:
        document = await self.collection.find_one({"order_id": order_id})
        
        if document:
            document["id"] = document.pop("_id")
            return Payment(**document)
            
        return None