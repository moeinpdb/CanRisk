# 🎗️ Gail Breast Cancer Risk Assessment API

API محاسبه ریسک سرطان سینه بر اساس مدل Gail (BCRA)

## 🚀 شروع سریع

### نصب

```bash
cd backend
pip install -r requirements.txt
```

### اجرا

```bash
# روش 1: با uvicorn مستقیم
uvicorn app.main:app --reload --port 8000

# روش 2: با run.py
python run.py
```

سپس به `http://localhost:8000/api/docs` بروید.

## 📋 ساختار پروژه

```
backend/
├── app/
│   ├── calculators/     # Gail model implementation
│   ├── models/          # Pydantic models
│   ├── routers/         # API endpoints
│   ├── services/        # Business logic
│   └── utils/           # Helpers
├── tests/               # Test suites
└── requirements.txt
```

## 🧪 تست‌ها

```bash
# اجرای تمام تست‌ها
pytest tests/ -v

# فقط parity tests
pytest tests/test_gail_parity.py -v -s

# اجرای اسکریپت parity
python scripts/parity_test_runner.py
```

## 📖 مستندات API

- **Swagger UI**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`

## 🔑 Endpoints اصلی

- `POST /api/gail/calculate` - محاسبه ریسک
- `GET /api/gail/info` - اطلاعات مدل
- `GET /api/gail/races` - لیست نژادها
- `GET /api/health` - Health check

## ⚠️ محدودیت‌ها

- سن: 35-85 سال
- بدون سابقه سرطان سینه
- بدون جهش BRCA1/BRCA2

## 📚 منابع

- [NCI BCRA Tool](https://bcrisktool.cancer.gov/)
- [Gail Model Paper](https://pubmed.ncbi.nlm.nih.gov/2593165/)
