# SplitBill API handoff สำหรับ Frontend

สถานะ: Backend มี endpoints ด้านล่างแล้ว เอกสารนี้สรุป contract ที่ implement และทดสอบผ่าน HTTP กับ PostgreSQL แยก ดู [backend plan](BACKEND-PLAN.md) สำหรับข้อตกลงและบริบท

ตัวอย่าง response ด้านล่างตรงกับ implementation ปัจจุบัน ควรทดสอบ frontend กับ API จริงเพิ่มเติม เพราะผลทดสอบ mock ไม่ยืนยันการเชื่อมต่อจริง

## Base path และ headers

Endpoints ของกลุ่มใช้ path ตามโจทย์ **ไม่มี `/api` หรือ `/api/v1` prefix**:

| Method | Path | การใช้งาน |
| --- | --- | --- |
| GET | `/groups` | รายการกลุ่มของผู้ใช้ |
| GET | `/groups/{group_id}` | ข้อมูลกลุ่มและสมาชิก |
| POST | `/groups/{group_id}/expenses` | สร้าง expense |
| GET | `/groups/{group_id}/expenses` | รายการ expense ที่ยังไม่ถูกลบ |
| DELETE | `/groups/{group_id}/expenses/{expense_id}` | ลบ expense แบบ soft delete |
| GET | `/groups/{group_id}/balances` | ยอดสุทธิของสมาชิกแต่ละคน |

ทุก request ต้องส่ง `X-User` เป็นชื่อผู้ใช้ เช่น `alice` สำหรับ POST สร้าง expense ต้องส่ง `Idempotency-Key` ที่ไม่ว่างเพิ่มด้วย:

```http
X-User: alice
Idempotency-Key: 7f3c2a10-dinner-0001
Content-Type: application/json
```

`X-User` เป็นวิธีระบุผู้ใช้ตามโจทย์ ไม่ใช่ authentication จริง ถ้า header หายไป ว่าง หรือไม่พบผู้ใช้ จะตอบ `400`

สำหรับ browser ค่า `CORS_ORIGINS` อนุญาต `http://localhost:3000` และ `http://127.0.0.1:3000` โดยค่าเริ่มต้น หาก frontend ใช้ origin อื่น ต้องตั้งค่า environment variable นี้เป็น JSON array ของ origins ที่อนุญาตก่อนเริ่ม backend

ข้อมูล seed ที่โจทย์กำหนด: `alice`, `bob`, `carol`, `dan`; กลุ่ม 1 `Chiang Mai trip` มี alice, bob, carol; กลุ่ม 2 `Office lunch` มี bob, dan

## รูปแบบ response

**ตกลงแล้ว:** response สำเร็จใช้ JSON object หรือ array โดยตรง ไม่มี `data` wrapper; ค่าเงินทุกค่าต้องเป็น string เช่น `"1000.00"` ไม่ใช่ JSON number

Expense response มีฟิลด์ `id`, `group_id`, `description`, `paid_by`, `amount`, `shares` และ `created_at` แล้ว รูปแบบ `shares` และฟิลด์ของ group/member/balance แสดงในตัวอย่างด้านล่าง

### GET /groups

```json
[
  { "id": 1, "name": "Chiang Mai trip" }
]
```

### GET /groups/1

```json
{
  "id": 1,
  "name": "Chiang Mai trip",
  "members": ["alice", "bob", "carol"]
}
```

### GET /groups/1/expenses

```json
[
  {
    "id": 1,
    "group_id": 1,
    "description": "Dinner at the night market",
    "paid_by": "alice",
    "amount": "1000.00",
    "shares": {
      "alice": "333.34",
      "bob": "333.33",
      "carol": "333.33"
    },
    "created_at": "2026-11-14T12:00:00Z"
  }
]
```

รายการเรียงจากใหม่ไปเก่า และเมื่อเวลาเท่ากันจะเรียง expense ID มากกว่าก่อน

### GET /groups/1/balances

```json
[
  { "member": "alice", "balance": "666.66" },
  { "member": "bob", "balance": "-333.33" },
  { "member": "carol", "balance": "-333.33" }
]
```

ค่าบวกหมายถึงสมาชิกคนนั้นเป็นฝ่ายได้รับเงินคืน ค่าลบหมายถึงเป็นฝ่ายค้างจ่าย Backend จะส่งสมาชิกทุกคน รวมผู้ที่มียอด `"0.00"` และ balances ของทั้งกลุ่มต้องรวมกันได้ `0.00` พอดี

## POST expense: equal split

```json
{
  "description": "Dinner at the night market",
  "paid_by": "alice",
  "amount": "1000.00",
  "split": {
    "type": "equal",
    "members": ["alice", "bob", "carol"]
  }
}
```

ลำดับสมาชิกมีผลต่อลำดับการแจกเศษสตางค์ ตัวอย่างนี้ได้ shares `333.34`, `333.33`, `333.33` ตามลำดับ รายชื่อที่ว่างหรือมีชื่อซ้ำถูกปฏิเสธ ถ้า `"0.01"` หารสามคน **อนุญาตให้บางคนได้ `"0.00"`**

## POST expense: exact split

```json
{
  "description": "Dinner at the night market",
  "paid_by": "alice",
  "amount": "1000.00",
  "split": {
    "type": "exact",
    "shares": {
      "alice": "500.00",
      "bob": "300.00",
      "carol": "200.00"
    }
  }
}
```

Exact share ทุกค่าต้อง **มากกว่า `0.00`** และรวมกันเท่ากับ `amount` พอดี

สำหรับทั้งสองรูปแบบ `amount` ต้องเป็น string ที่มากกว่าศูนย์ มีทศนิยมไม่เกินสองตำแหน่ง และไม่เกินช่วง `NUMERIC(12,2)` payer และผู้ร่วม split ทุกคนต้องเป็นสมาชิกกลุ่ม แต่ payer ไม่จำเป็นต้องอยู่ในรายการผู้ร่วม split การคำนวณฝั่ง frontend ควรหลีกเลี่ยง floating-point error เพื่อให้ preview ตรงกับ backend

## Idempotency

- สร้าง expense ใหม่สำเร็จ: **201** พร้อม expense ที่สร้าง
- ส่ง key เดิมซ้ำในกลุ่มเดิม โดย request ใหม่ผ่าน validation: **200** พร้อม expense เดิม โดยไม่สร้างรายการใหม่ แม้ body ใหม่จะต่างจากเดิม
- Request ใหม่ไม่ผ่าน validation: **400** แม้ key เคยใช้แล้ว
- Key มีขอบเขตระดับกลุ่ม สมาชิกคนอื่นในกลุ่มเดียวกันสามารถ replay key เดิมได้
- Backend ตรวจสิทธิ์กลุ่มก่อนคืนข้อมูล ผู้ที่ไม่ใช่สมาชิกได้รับ **404**
- หาก expense เดิมถูก soft-delete แล้ว การ replay key เดิมยังคืน expense เดิม แต่ไม่สร้างใหม่และไม่คืนสถานะรายการนั้น

Frontend ควรเก็บ key เดิมไว้เมื่อ retry การสร้าง expense รายการเดิม และใช้ key ใหม่สำหรับ expense ใหม่

## การลบ expense

`DELETE /groups/{group_id}/expenses/{expense_id}`:

- Payer ลบสำเร็จ: **204 No Content** ไม่มี response body
- สมาชิกกลุ่มที่ไม่ใช่ payer พยายามลบ expense ที่ยัง active: **403**
- ลบรายการเดิมซ้ำหลังลบสำเร็จ: **404**
- ผู้ที่ไม่ใช่สมาชิกกลุ่ม: **404**

การลบเป็น soft delete: record ยังคงอยู่ แต่ไม่แสดงในรายการ expense ปกติ และไม่นำมาคิด balances

## Error response

**ตกลงรูปแบบแล้ว:**

```json
{
  "error": {
    "code": "bad_request",
    "message": "Exact shares must add up to the expense amount"
  }
}
```

Error codes ปัจจุบัน ได้แก่ `bad_request`, `not_found`, `forbidden`, `http_error` และ `internal_error` ส่วนสถานะหลักคือ `400` สำหรับ request ไม่ถูกต้อง, `403` สำหรับสมาชิกที่ไม่ใช่ payer พยายามลบ expense ที่ยัง active และ `404` สำหรับผู้ที่ไม่ใช่สมาชิกกลุ่มหรือ resource ที่ไม่พบ
