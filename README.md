# IoDT2 Thing Description

**IoDT2 Thing Description**, DTDL (Digital Twins Definition Language) tabanli dijital ikiz yonetim sistemidir. YAML formatini kullanarak dijital ikizleri olusturmaniza, yonetmenize ve sorgulamaniza olanak tanir.

## Hizli Baslangic (Quick Start)

```bash
# 1. Projeyi klonlayin
git clone <repository-url>
cd thing-for-twinscale

# 2. Docker ile baslatin (Onerilen)
docker-compose up -d

# 3. Tarayicinizda acin
# Frontend: http://localhost:3005
# API Docs: http://localhost:3015/docs
```

---

## Icerikler

- [Ozellikler](#ozellikler)
- [Mimari](#mimari)
- [Kurulum](#kurulum)
  - [Docker ile Kurulum (Onerilen)](#docker-ile-kurulum-onerilen)
  - [Manuel Kurulum](#manuel-kurulum)
- [Kullanim](#kullanim)
  - [Docker ile Kullanim](#docker-ile-kullanim)
  - [Manuel Kullanim](#manuel-kullanim)
  - [DTDL Islemleri](#dtdl-islemleri)
  - [Thing Yonetimi](#thing-yonetimi)
  - [YAML Sorgulari](#yaml-sorgulari)
- [DTDL Kutuphanesi](#dtdl-kutuphanesi)
- [API Dokumantasyonu](#api-dokumantasyonu)
- [Test](#test)
- [Sorun Giderme](#sorun-giderme-troubleshooting)
- [Proje Yapisi](#proje-yapisi)

---

## Ozellikler

- **DTDL Destegi**: Standart DTDL (v3) arayuzleri ile uyumlu
- **YAML Format**: Insan okunabilir YAML formatinda dijital ikiz tanimlari
- **Moduler Kutuphane**: Cevresel sensorler, sismik algilayicilar, hava kalitesi sensorleri
- **Dogrulama**: DTDL semalarina gore otomatik dogrulama
- **Donusturme**: DTDL <-> YAML cift yonlu donusum
- **REST API**: FastAPI tabanli modern REST API
- **React Frontend**: Kullanici dostu web arayuzu

---

## Mimari

### Backend (Python/FastAPI)

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   └── v2/
│   │       ├── dtdl.py   # DTDL arayuz yonetimi
│   │       ├── twin.py   # Thing yonetimi
│   │       ├── fuseki.py # Fuseki RDF islemleri
│   │       └── tenants.py # Tenant yonetimi
│   ├── services/         # Is mantigi servisleri
│   │   ├── dtdl_loader_service.py      # DTDL yukleme ve cache
│   │   ├── dtdl_converter_service.py   # DTDL <-> YAML donusum
│   │   ├── dtdl_validator_service.py   # DTDL dogrulama
│   │   ├── twin_generator_service.py   # Thing olusturma
│   │   ├── twin_rdf_service.py         # RDF islemleri
│   │   ├── tenant_manager.py           # Tenant yonetimi
│   │   └── location_service.py         # Konum servisi
│   ├── dtdl_library/     # DTDL arayuz kutuphanesi
│   │   ├── base/         # Temel arayuzler (BaseTwin, SensorTwin, vb.)
│   │   ├── domain/       # Alan-spesifik arayuzler
│   │   │   ├── environmental/  # Cevresel sensorler
│   │   │   ├── air_quality/    # Hava kalitesi sensorleri
│   │   │   └── seismic/        # Sismik algilayicilar
│   │   └── registry.json # Arayuz kayit defteri
│   ├── models/           # SQLAlchemy modelleri
│   ├── schemas/          # Pydantic semalari
│   └── core/             # Temel yapilandirma
├── tests/                # Test dosyalari
├── scripts/              # Yardimci scriptler
└── main.py               # Uygulama giris noktasi
```

### Frontend (React/Vite)

```
frontend/
├── src/
│   ├── api/              # API istemcileri
│   ├── components/       # React bilesenleri
│   │   ├── dtdl/         # DTDL bilesenleri
│   │   └── twin/         # Thing bilesenleri
│   ├── pages/            # Sayfa bilesenleri
│   │   └── twin/         # Thing sayfalari
│   ├── services/         # Servis katmani
│   └── locales/          # i18n cevirileri
└── ...
```

---

## Kurulum

### Docker ile Kurulum (Onerilen)

En hizli ve kolay yol! Sadece birkac komutla tum sistemi ayaga kaldirin.

#### Gereksinimler
- **Docker** 20.10+
- **Docker Compose** 2.0+

#### Kurulum Adimlari

```bash
# 1. Tum servisleri baslat (Backend, Frontend, Fuseki)
docker-compose up -d

# 2. Loglari izle (opsiyonel)
docker-compose logs -f

# 3. Durum kontrolu
docker-compose ps
```

Sisteminiz su adreslerde calisiyor:

- **Frontend**: http://localhost:3005
- **Backend API**: http://localhost:3015
- **Fuseki (RDF Store)**: http://localhost:3030
- **API Docs**: http://localhost:3015/docs

#### Docker Komutlari

```bash
# Servisleri durdur
docker-compose down

# Servisleri durdur ve verileri sil
docker-compose down -v

# Servisleri yeniden baslat
docker-compose restart

# Belirli bir servisi yeniden baslat
docker-compose restart backend

# Loglari goruntule
docker-compose logs backend
docker-compose logs frontend
docker-compose logs fuseki

# Container'a baglan (debugging)
docker-compose exec backend bash
docker-compose exec frontend sh

# Servisleri guncelle (yeni degisiklikler icin)
docker-compose up -d --build
```

#### Health Check

Tum servisler otomatik health check yapilandirmasi ile geliyor:

```bash
# Servis durumunu kontrol et
docker-compose ps

# Detayli health durumu
docker inspect iodt2-thing-backend | grep -A 10 "Health"
docker inspect iodt2-thing-frontend | grep -A 10 "Health"
docker inspect iodt2-thing-fuseki | grep -A 10 "Health"
```

---

### Manuel Kurulum

Gelistirme ortami icin manuel kurulum:

#### Gereksinimler

- **Python** 3.9+
- **Node.js** 16+
- **npm** veya **yarn**

#### Backend Kurulumu

```bash
# Backend dizinine gidin
cd backend

# Sanal ortam olusturun
python -m venv venv

# Sanal ortami etkinlestirin
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Bagimliliklari yukleyin
pip install -r requirements.txt

# Ortam degiskenlerini yapilandirin
cp .env.example .env
# .env dosyasini duzenleyin
```

#### Frontend Kurulumu

```bash
# Frontend dizinine gidin
cd frontend

# Bagimliliklari yukleyin
npm install

# Ortam degiskenlerini yapilandirin
cp .env.example .env
# .env dosyasini duzenleyin
```

---

## Kullanim

### Docker ile Kullanim

```bash
# Tum servisleri baslat
docker-compose up -d

# Uygulamaya erisim
# Frontend: http://localhost:3005
# Backend: http://localhost:3015
# API Docs: http://localhost:3015/docs
```

### Manuel Kullanim

#### Backend API'yi Baslatma

```bash
cd backend
python main.py
```

Backend varsayilan olarak `http://localhost:3015` adresinde calisir.

#### Frontend'i Baslatma

```bash
cd frontend
npm run dev
```

Frontend varsayilan olarak `http://localhost:5173` adresinde calisir.

---

## DTDL Islemleri

### 1. Mevcut DTDL Arayuzlerini Listeleme

**API Endpoint:** `GET /api/v2/dtdl/interfaces`

```bash
curl http://localhost:3015/api/v2/dtdl/interfaces
```

**Yanit:**
```json
[
  {
    "dtmi": "dtmi:twinscale:BaseTwin;1",
    "displayName": "Base Digital Twin",
    "description": "Base interface for all digital twins",
    "category": "base"
  },
  {
    "dtmi": "dtmi:twinscale:SensorTwin;1",
    "displayName": "Sensor Twin",
    "description": "Base interface for sensor digital twins",
    "category": "base"
  }
]
```

### 2. DTDL Arayuz Detaylarini Goruntuleme

**API Endpoint:** `GET /api/v2/dtdl/interfaces/{dtmi}`

```bash
curl "http://localhost:3015/api/v2/dtdl/interfaces/dtmi:twinscale:environmental:TemperatureSensor;1"
```

### 3. DTDL Gereksinimlerini Ogrenme

**API Endpoint:** `GET /api/v2/dtdl/interfaces/{dtmi}/requirements`

```bash
curl "http://localhost:3015/api/v2/dtdl/interfaces/dtmi:twinscale:environmental:TemperatureSensor;1/requirements"
```

**Yanit:**
```json
{
  "requiredProperties": [
    {
      "name": "temperature",
      "schema": "double",
      "description": "Current temperature reading in Celsius"
    }
  ],
  "requiredTelemetry": [
    {
      "name": "temperatureReading",
      "schema": "double"
    }
  ],
  "requiredCommands": [],
  "inheritedFrom": ["dtmi:twinscale:SensorTwin;1"]
}
```

### 4. DTDL'den YAML Sablonu Olusturma

**API Endpoint:** `POST /api/v2/dtdl/convert/to-twinscale`

```bash
curl -X POST "http://localhost:3015/api/v2/dtdl/convert/to-twinscale" \
  -H "Content-Type: application/json" \
  -d '{
    "dtmi": "dtmi:twinscale:environmental:TemperatureSensor;1",
    "thing_name": "OfficeTemperatureSensor",
    "tenant_id": "my-tenant"
  }'
```

---

## Thing Yonetimi

### 1. Thing Olusturma (YAML)

**API Endpoint:** `POST /api/v2/twin/things`

**YAML Thing Tanimi:**
```yaml
thing:
  name: MyOfficeTemperatureSensor
  interface: TemperatureSensor
  version: "1.0"
  tenant: office-building
  properties:
    temperature: 23.5
    unit: celsius
    location: "Office Room 101"
  metadata:
    dtdl:
      dtmi: dtmi:twinscale:environmental:TemperatureSensor;1
    created_by: user@example.com
```

```bash
curl -X POST "http://localhost:3015/api/v2/twin/things" \
  -H "Content-Type: application/x-yaml" \
  --data-binary @thing.yaml
```

### 2. Thing Listeleme

**API Endpoint:** `GET /api/v2/twin/things`

**Filtreleme Parametreleri:**
- `tenant`: Tenant ID'ye gore filtrele
- `interface`: Arayuz adina gore filtrele
- `limit`: Sonuc sayisini sinirla (varsayilan: 100)
- `offset`: Pagination icin offset

```bash
# Tum things
curl "http://localhost:3015/api/v2/twin/things"

# Tenant'a gore filtrele
curl "http://localhost:3015/api/v2/twin/things?tenant=office-building"

# Interface'e gore filtrele
curl "http://localhost:3015/api/v2/twin/things?interface=TemperatureSensor"
```

### 3. Thing Detaylarini Goruntuleme

**API Endpoint:** `GET /api/v2/twin/things/{thing_id}`

```bash
curl "http://localhost:3015/api/v2/twin/things/1"
```

### 4. Thing Guncelleme

**API Endpoint:** `PUT /api/v2/twin/things/{thing_id}`

```bash
curl -X PUT "http://localhost:3015/api/v2/twin/things/1" \
  -H "Content-Type: application/x-yaml" \
  --data-binary @updated-thing.yaml
```

### 5. Thing Silme

**API Endpoint:** `DELETE /api/v2/twin/things/{thing_id}`

```bash
curl -X DELETE "http://localhost:3015/api/v2/twin/things/1"
```

---

## YAML Sorgulari

### YAML Icerigini Arama

YAML iceriginde anahtar-deger ciftlerini aramak icin sorgulama ozellikleri:

**API Endpoint:** `GET /api/v2/twin/things/search`

```bash
# Belirli bir sicaklik degerine sahip tum sensorler
curl "http://localhost:3015/api/v2/twin/things/search?query=properties.temperature&value=23.5"

# Belirli bir konumdaki tum cihazlar
curl "http://localhost:3015/api/v2/twin/things/search?query=properties.location&value=Office%20Room%20101"
```

---

## DTDL Kutuphanesi

### Mevcut Arayuzler

#### Base Arayuzler
- **BaseTwin** (`dtmi:twinscale:BaseTwin;1`): Tum dijital ikizler icin temel arayuz
- **SensorTwin** (`dtmi:twinscale:SensorTwin;1`): Sensorler icin temel arayuz
- **ActuatorTwin** (`dtmi:twinscale:ActuatorTwin;1`): Aktuatorler icin temel arayuz
- **GatewayTwin** (`dtmi:twinscale:GatewayTwin;1`): Ag gecitleri icin temel arayuz

#### Cevresel Sensorler (Environmental)
- **TemperatureSensor** (`dtmi:twinscale:environmental:TemperatureSensor;1`)
- **HumiditySensor** (`dtmi:twinscale:environmental:HumiditySensor;1`)
- **WeatherStation** (`dtmi:twinscale:environmental:WeatherStation;1`)

#### Hava Kalitesi Sensorleri (Air Quality)
- **PM25Sensor** (`dtmi:twinscale:air_quality:PM25Sensor;1`)

#### Sismik Sensorler (Seismic)
- **Building** (`dtmi:twinscale:seismic:Building;1`)
- **Street** (`dtmi:twinscale:seismic:Street;1`)
- **BaseStation** (`dtmi:twinscale:seismic:BaseStation;1`)
- **SeismicSensor** (`dtmi:twinscale:seismic:SeismicSensor;1`)

### Yeni DTDL Arayuzu Ekleme

1. **DTDL JSON dosyasini olusturun:**

```json
{
  "@context": "dtmi:dtdl:context;3",
  "@id": "dtmi:twinscale:domain:MySensor;1",
  "@type": "Interface",
  "displayName": "My Custom Sensor",
  "description": "Description of my sensor",
  "extends": "dtmi:twinscale:SensorTwin;1",
  "contents": [
    {
      "@type": "Property",
      "name": "myProperty",
      "schema": "double",
      "description": "My custom property"
    }
  ]
}
```

2. **Dosyayi uygun dizine kaydedin:**
```
backend/app/dtdl_library/domain/my_domain/MySensor.json
```

3. **registry.json dosyasini guncelleyin:**
```json
{
  "dtmi": "dtmi:twinscale:domain:MySensor;1",
  "displayName": "My Custom Sensor",
  "description": "Description of my sensor",
  "filePath": "domain/my_domain/MySensor.json",
  "category": "domain",
  "tags": ["sensor", "custom"]
}
```

4. **Backend'i yeniden baslatin:**
```bash
python main.py
```

---

## API Dokumantasyonu

Backend calistiginda, interaktif API dokumantasyonuna su adresten erisebilirsiniz:

- **Swagger UI**: http://localhost:3015/docs
- **ReDoc**: http://localhost:3015/redoc

---

## Test

### Test Dosyalarini Calistirma

```bash
cd backend

# Tum testleri calistir
pytest tests/

# Belirli bir test dosyasini calistir
pytest tests/test_dtdl_loader.py

# Verbose cikti ile
pytest tests/ -v

# Coverage raporu ile
pytest tests/ --cov=app
```

### Docker Container'da Test

```bash
# Backend container'inda testleri calistir
docker-compose exec backend pytest tests/ -v
```

---

## Sorun Giderme (Troubleshooting)

### Docker ile Ilgili Sorunlar

#### Container'lar baslamiyor

```bash
# Loglari kontrol edin
docker-compose logs

# Belirli bir servisin logunu kontrol edin
docker-compose logs backend

# Container'lari temizleyin ve yeniden baslatin
docker-compose down -v
docker-compose up -d --build
```

#### Port zaten kullanimda

```bash
# Cakisan portlari kontrol edin
# Windows:
netstat -ano | findstr :3015
netstat -ano | findstr :3005
netstat -ano | findstr :3030

# Linux/Mac:
lsof -i :3015
lsof -i :3005
lsof -i :3030
```

#### Backend Fuseki'ye baglanamiyorsa

```bash
# Fuseki health check
curl http://localhost:3030/$/ping

# Fuseki loglarini kontrol edin
docker-compose logs fuseki

# Network kontrolu
docker network inspect iodt2-network
```

#### Frontend backend'e erisemiyorsa

```bash
# Backend baglantisini test edin (container icinden)
docker-compose exec frontend curl http://backend:3015/health

# Frontend'i yeniden build edin
docker-compose up -d --build frontend
```

### Genel Sorunlar

#### DTDL arayuzu yuklenmiyor

```bash
# Registry dosyasini kontrol edin
cat backend/app/dtdl_library/registry.json

# DTDL dosyasinin varligini kontrol edin
ls -la backend/app/dtdl_library/domain/

# Backend loglarini kontrol edin
docker-compose logs backend | grep -i dtdl
```

#### CORS hatasi

```bash
# Backend .env dosyasini kontrol edin
grep CORS backend/.env

# CORS_ORIGINS ortam degiskenini guncelleyin
CORS_ORIGINS=http://localhost,http://localhost:3005,http://localhost:5173
```

---

## Proje Yapisi

```
thing-for-twinscale/
├── backend/                      # Python/FastAPI backend
│   ├── app/
│   │   ├── api/                  # API endpoints
│   │   │   └── v2/
│   │   │       ├── dtdl.py       # DTDL API
│   │   │       ├── twin.py       # Thing API
│   │   │       ├── fuseki.py     # Fuseki API
│   │   │       └── tenants.py    # Tenant API
│   │   ├── core/                 # Temel yapilandirma
│   │   │   ├── config.py         # Ayarlar
│   │   │   ├── database.py       # Veritabani
│   │   │   └── twin_ontology.py  # Ontoloji tanimlari
│   │   ├── dtdl_library/         # DTDL arayuz kutuphanesi
│   │   │   ├── base/             # Temel arayuzler
│   │   │   │   ├── BaseTwin.json
│   │   │   │   ├── SensorTwin.json
│   │   │   │   ├── ActuatorTwin.json
│   │   │   │   └── GatewayTwin.json
│   │   │   ├── domain/           # Alan-spesifik arayuzler
│   │   │   │   ├── environmental/
│   │   │   │   ├── air_quality/
│   │   │   │   └── seismic/
│   │   │   └── registry.json
│   │   ├── models/               # SQLAlchemy ORM modelleri
│   │   ├── schemas/              # Pydantic semalari
│   │   └── services/             # Is mantigi servisleri
│   ├── tests/                    # Test dosyalari
│   ├── scripts/                  # Yardimci scriptler
│   ├── main.py                   # Uygulama giris noktasi
│   ├── requirements.txt          # Python bagimliliklari
│   └── Dockerfile                # Backend Docker image
│
├── frontend/                     # React/Vite frontend
│   ├── src/
│   │   ├── api/                  # API istemcileri
│   │   ├── components/           # React bilesenleri
│   │   │   ├── dtdl/             # DTDL UI bilesenleri
│   │   │   └── twin/             # Thing UI bilesenleri
│   │   ├── pages/                # Sayfa bilesenleri
│   │   │   └── twin/             # Thing sayfalari
│   │   ├── services/             # Servis katmani
│   │   └── locales/              # i18n cevirileri
│   ├── package.json              # Node bagimliliklari
│   ├── vite.config.js            # Vite yapilandirmasi
│   ├── Dockerfile                # Frontend Docker image
│   └── nginx.conf                # Nginx yapilandirmasi
│
├── docker-compose.yml            # Docker Compose yapilandirmasi
└── README.md                     # Bu dosya
```

### Docker Servisleri

Docker Compose ile 3 servis ayaga kaldirilir:

1. **fuseki** (Port 3030): Apache Jena Fuseki RDF Triple Store
   - SPARQL endpoint
   - RDF veri saklama
   - 2GB JVM heap memory

2. **backend** (Port 3015): FastAPI backend
   - REST API
   - DTDL yonetimi
   - Thing YAML isleme
   - SQLite veritabani

3. **frontend** (Port 3005): React + Nginx
   - SPA web arayuzu
   - Nginx reverse proxy

---

## Katkida Bulunma

Katkilarinizi bekliyoruz! Lutfen:

1. Fork yapin
2. Feature branch olusturun (`git checkout -b feature/amazing-feature`)
3. Degisikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request acin

---

## Lisans

Bu proje MIT lisansi altinda lisanslanmistir.

---

## Tesekkurler

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI kutuphanesi
- [DTDL](https://github.com/Azure/opendigitaltwins-dtdl) - Digital Twins Definition Language
