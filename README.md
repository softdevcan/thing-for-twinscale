# TwinScale-Lite

**TwinScale-Lite**, DTDL (Digital Twins Definition Language) tabanlı dijital ikiz yönetim sistemidir. TwinScale YAML formatını kullanarak dijital ikizleri oluşturmanıza, yönetmenize ve sorgulamanıza olanak tanır.

## ⚡ Hızlı Başlangıç (Quick Start)

```bash
# 1. Projeyi klonlayın
git clone <repository-url>
cd thing-for-twinscale

# 2. Docker ile başlatın (Önerilen)
docker-compose up -d

# 3. Tarayıcınızda açın
# Frontend: http://localhost:3005
# API Docs: http://localhost:3015/docs
```

**Hepsi bu kadar!** 🎉

---

## 📋 İçindekiler

- [Özellikler](#özellikler)
- [Mimari](#mimari)
- [Kurulum](#kurulum)
  - [Docker ile Kurulum (Önerilen)](#-docker-ile-kurulum-önerilen)
  - [Manuel Kurulum](#-manuel-kurulum)
- [Kullanım](#kullanım)
  - [Docker ile Kullanım](#-docker-ile-kullanım)
  - [Manuel Kullanım](#-manuel-kullanım)
  - [DTDL İşlemleri](#dtdl-işlemleri)
  - [TwinScale Thing Yönetimi](#twinscale-thing-yönetimi)
  - [YAML Sorguları](#yaml-sorguları)
- [DTDL Kütüphanesi](#dtdl-kütüphanesi)
- [API Dokümantasyonu](#api-dokümantasyonu)
- [Test](#test)
- [Sorun Giderme](#-sorun-giderme-troubleshooting)
- [Proje Yapısı](#proje-yapısı)

---

## ✨ Özellikler

- **DTDL Desteği**: Standart DTDL (v3) arayüzleri ile uyumlu
- **TwinScale YAML**: İnsan okunabilir YAML formatında dijital ikiz tanımları
- **Modüler Kütüphane**: Çevresel sensörler, sismik algılayıcılar, hava kalitesi sensörleri
- **Doğrulama**: DTDL şemalarına göre otomatik doğrulama
- **Dönüştürme**: DTDL ↔ TwinScale YAML çift yönlü dönüşüm
- **REST API**: FastAPI tabanlı modern REST API
- **React Frontend**: Kullanıcı dostu web arayüzü

---

## 🏗️ Mimari

### Backend (Python/FastAPI)

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   └── v2/
│   │       ├── dtdl.py   # DTDL arayüz yönetimi
│   │       └── twinscale.py  # TwinScale Thing yönetimi
│   ├── services/         # İş mantığı servisleri
│   │   ├── dtdl_loader_service.py      # DTDL yükleme ve cache
│   │   ├── dtdl_converter_service.py   # DTDL ↔ TwinScale dönüşüm
│   │   └── dtdl_validator_service.py   # DTDL doğrulama
│   ├── dtdl_library/     # DTDL arayüz kütüphanesi
│   │   ├── base/         # Temel arayüzler (BaseTwin, SensorTwin, vb.)
│   │   ├── domain/       # Alan-spesifik arayüzler
│   │   │   ├── environmental/  # Çevresel sensörler
│   │   │   ├── air_quality/    # Hava kalitesi sensörleri
│   │   │   └── seismic/        # Sismik algılayıcılar
│   │   └── registry.json # Arayüz kayıt defteri
│   ├── models/           # SQLAlchemy modelleri
│   └── schemas/          # Pydantic şemaları
├── tests/                # Test dosyaları
└── main.py               # Uygulama giriş noktası
```

### Frontend (React/Vite)

```
frontend/
├── src/
│   ├── api/              # API istemcileri
│   ├── components/       # React bileşenleri
│   │   └── dtdl/         # DTDL bileşenleri
│   ├── pages/            # Sayfa bileşenleri
│   └── locales/          # i18n çevirileri
└── ...
```

---

## 🚀 Kurulum

### 🐳 Docker ile Kurulum (Önerilen)

En hızlı ve kolay yol! Sadece birkaç komutla tüm sistemi ayağa kaldırın.

#### Gereksinimler
- **Docker** 20.10+
- **Docker Compose** 2.0+

#### Kurulum Adımları

```bash
# 1. Tüm servisleri başlat (Backend, Frontend, Fuseki)
docker-compose up -d

# 2. Logları izle (opsiyonel)
docker-compose logs -f

# 3. Durum kontrolü
docker-compose ps
```

**Hepsi bu kadar!** Sisteminiz şu adreslerde çalışıyor:

- 🌐 **Frontend**: http://localhost:3005
- 🔌 **Backend API**: http://localhost:3015
- 📊 **Fuseki (RDF Store)**: http://localhost:3030
- 📖 **API Docs**: http://localhost:3015/docs

#### Docker Komutları

```bash
# Servisleri durdur
docker-compose down

# Servisleri durdur ve verileri sil
docker-compose down -v

# Servisleri yeniden başlat
docker-compose restart

# Belirli bir servisi yeniden başlat
docker-compose restart backend

# Logları görüntüle
docker-compose logs backend
docker-compose logs frontend
docker-compose logs fuseki

# Container'a bağlan (debugging)
docker-compose exec backend bash
docker-compose exec frontend sh

# Servisleri güncelle (yeni değişiklikler için)
docker-compose up -d --build
```

#### Health Check

Tüm servisler otomatik health check yapılandırması ile geliyor:

```bash
# Servis durumunu kontrol et
docker-compose ps

# Detaylı health durumu
docker inspect twinscale-backend | grep -A 10 "Health"
docker inspect twinscale-frontend | grep -A 10 "Health"
docker inspect twinscale-fuseki | grep -A 10 "Health"
```

---

### 🔧 Manuel Kurulum

Geliştirme ortamı için manuel kurulum:

#### Gereksinimler

- **Python** 3.9+
- **Node.js** 16+
- **npm** veya **yarn**

#### Backend Kurulumu

```bash
# Backend dizinine gidin
cd backend

# Sanal ortam oluşturun
python -m venv venv

# Sanal ortamı etkinleştirin
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Ortam değişkenlerini yapılandırın
cp .env.example .env
# .env dosyasını düzenleyin
```

#### Frontend Kurulumu

```bash
# Frontend dizinine gidin
cd frontend

# Bağımlılıkları yükleyin
npm install

# Ortam değişkenlerini yapılandırın
cp .env.example .env
# .env dosyasını düzenleyin
```

---

## 💻 Kullanım

### 🐳 Docker ile Kullanım

```bash
# Tüm servisleri başlat
docker-compose up -d

# Uygulamaya erişim
# Frontend: http://localhost:3005
# Backend: http://localhost:3015
# API Docs: http://localhost:3015/docs
```

### 🔧 Manuel Kullanım

#### Backend API'yi Başlatma

```bash
cd backend
python main.py
```

Backend varsayılan olarak `http://localhost:3015` adresinde çalışır.

#### Frontend'i Başlatma

```bash
cd frontend
npm run dev
```

Frontend varsayılan olarak `http://localhost:5173` adresinde çalışır.

---

## 🔧 DTDL İşlemleri

### 1. Mevcut DTDL Arayüzlerini Listeleme

**API Endpoint:** `GET /api/v2/dtdl/interfaces`

**cURL Örneği:**
```bash
curl http://localhost:3015/api/v2/dtdl/interfaces
```

**Python Örneği:**
```python
import requests

response = requests.get("http://localhost:3015/api/v2/dtdl/interfaces")
interfaces = response.json()

for interface in interfaces:
    print(f"{interface['dtmi']}: {interface['displayName']}")
```

**Yanıt:**
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

### 2. DTDL Arayüz Detaylarını Görüntüleme

**API Endpoint:** `GET /api/v2/dtdl/interfaces/{dtmi}`

**cURL Örneği:**
```bash
curl "http://localhost:3015/api/v2/dtdl/interfaces/dtmi:twinscale:environmental:TemperatureSensor;1"
```

**Python Örneği:**
```python
dtmi = "dtmi:twinscale:environmental:TemperatureSensor;1"
response = requests.get(f"http://localhost:3015/api/v2/dtdl/interfaces/{dtmi}")
interface_details = response.json()

print(f"Arayüz: {interface_details['displayName']}")
print(f"Açıklama: {interface_details['description']}")
print(f"Özellikler: {len(interface_details.get('contents', []))}")
```

### 3. DTDL Gereksinimlerini Öğrenme

**API Endpoint:** `GET /api/v2/dtdl/interfaces/{dtmi}/requirements`

**cURL Örneği:**
```bash
curl "http://localhost:3015/api/v2/dtdl/interfaces/dtmi:twinscale:environmental:TemperatureSensor;1/requirements"
```

**Yanıt:**
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

### 4. DTDL'den TwinScale YAML Şablonu Oluşturma

**API Endpoint:** `POST /api/v2/dtdl/convert/to-twinscale`

**cURL Örneği:**
```bash
curl -X POST "http://localhost:3015/api/v2/dtdl/convert/to-twinscale" \
  -H "Content-Type: application/json" \
  -d '{
    "dtmi": "dtmi:twinscale:environmental:TemperatureSensor;1",
    "thing_name": "OfficeTemperatureSensor",
    "tenant_id": "my-tenant"
  }'
```

**Python Örneği:**
```python
payload = {
    "dtmi": "dtmi:twinscale:environmental:TemperatureSensor;1",
    "thing_name": "OfficeTemperatureSensor",
    "tenant_id": "my-tenant"
}

response = requests.post(
    "http://localhost:3015/api/v2/dtdl/convert/to-twinscale",
    json=payload
)

result = response.json()
print("Interface YAML:")
print(result["interface_yaml"])
print("\nInstance YAML:")
print(result["instance_yaml"])
```

**Dönen YAML Şablonu:**
```yaml
# interface_yaml
interface:
  name: TemperatureSensor
  version: "1.0"
  extends: SensorTwin
  properties:
    - name: temperature
      type: double
      description: Current temperature reading in Celsius
  telemetry:
    - name: temperatureReading
      type: double

# instance_yaml
thing:
  name: OfficeTemperatureSensor
  interface: TemperatureSensor
  version: "1.0"
  tenant: my-tenant
  properties:
    temperature: 0.0
  metadata:
    dtdl:
      dtmi: dtmi:twinscale:environmental:TemperatureSensor;1
```

---

## 📦 TwinScale Thing Yönetimi

### 1. Thing Oluşturma (YAML)

**API Endpoint:** `POST /api/v2/twinscale/things`

**YAML Thing Tanımı:**
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

**cURL Örneği:**
```bash
# YAML dosyasını kaydedin: thing.yaml
curl -X POST "http://localhost:3015/api/v2/twinscale/things" \
  -H "Content-Type: application/x-yaml" \
  --data-binary @thing.yaml
```

**Python Örneği:**
```python
import yaml

thing_data = {
    "thing": {
        "name": "MyOfficeTemperatureSensor",
        "interface": "TemperatureSensor",
        "version": "1.0",
        "tenant": "office-building",
        "properties": {
            "temperature": 23.5,
            "unit": "celsius",
            "location": "Office Room 101"
        },
        "metadata": {
            "dtdl": {
                "dtmi": "dtmi:twinscale:environmental:TemperatureSensor;1"
            },
            "created_by": "user@example.com"
        }
    }
}

# YAML string'e çevir
yaml_str = yaml.dump(thing_data)

response = requests.post(
    "http://localhost:3015/api/v2/twinscale/things",
    headers={"Content-Type": "application/x-yaml"},
    data=yaml_str
)

created_thing = response.json()
print(f"Thing oluşturuldu: {created_thing['name']} (ID: {created_thing['id']})")
```

### 2. Thing Listeleme

**API Endpoint:** `GET /api/v2/twinscale/things`

**Filtreleme Parametreleri:**
- `tenant`: Tenant ID'ye göre filtrele
- `interface`: Arayüz adına göre filtrele
- `limit`: Sonuç sayısını sınırla (varsayılan: 100)
- `offset`: Pagination için offset

**cURL Örneği:**
```bash
# Tüm things
curl "http://localhost:3015/api/v2/twinscale/things"

# Tenant'a göre filtrele
curl "http://localhost:3015/api/v2/twinscale/things?tenant=office-building"

# Interface'e göre filtrele
curl "http://localhost:3015/api/v2/twinscale/things?interface=TemperatureSensor"
```

**Python Örneği:**
```python
# Belirli bir tenant'ın tüm sensörleri
params = {
    "tenant": "office-building",
    "interface": "TemperatureSensor"
}

response = requests.get(
    "http://localhost:3015/api/v2/twinscale/things",
    params=params
)

things = response.json()
for thing in things:
    print(f"{thing['name']}: {thing['properties'].get('temperature')}°C")
```

### 3. Thing Detaylarını Görüntüleme

**API Endpoint:** `GET /api/v2/twinscale/things/{thing_id}`

**cURL Örneği:**
```bash
curl "http://localhost:3015/api/v2/twinscale/things/1"
```

**Python Örneği:**
```python
thing_id = 1
response = requests.get(f"http://localhost:3015/api/v2/twinscale/things/{thing_id}")
thing = response.json()

print(f"Thing: {thing['name']}")
print(f"YAML:\n{thing['yaml_content']}")
```

### 4. Thing Güncelleme

**API Endpoint:** `PUT /api/v2/twinscale/things/{thing_id}`

**YAML Güncellemesi:**
```yaml
thing:
  name: MyOfficeTemperatureSensor
  interface: TemperatureSensor
  version: "1.0"
  tenant: office-building
  properties:
    temperature: 25.8  # Güncellenen değer
    unit: celsius
    location: "Office Room 101"
  metadata:
    dtdl:
      dtmi: dtmi:twinscale:environmental:TemperatureSensor;1
    updated_at: "2026-02-06T10:30:00Z"
```

**cURL Örneği:**
```bash
curl -X PUT "http://localhost:3015/api/v2/twinscale/things/1" \
  -H "Content-Type: application/x-yaml" \
  --data-binary @updated-thing.yaml
```

**Python Örneği:**
```python
thing_id = 1

# Mevcut thing'i al
thing = requests.get(f"http://localhost:3015/api/v2/twinscale/things/{thing_id}").json()

# YAML'i parse et ve güncelle
import yaml
thing_data = yaml.safe_load(thing['yaml_content'])
thing_data['thing']['properties']['temperature'] = 25.8

# Güncellenmiş YAML'i gönder
updated_yaml = yaml.dump(thing_data)
response = requests.put(
    f"http://localhost:3015/api/v2/twinscale/things/{thing_id}",
    headers={"Content-Type": "application/x-yaml"},
    data=updated_yaml
)

print("Thing güncellendi:", response.json()['name'])
```

### 5. Thing Silme

**API Endpoint:** `DELETE /api/v2/twinscale/things/{thing_id}`

**cURL Örneği:**
```bash
curl -X DELETE "http://localhost:3015/api/v2/twinscale/things/1"
```

**Python Örneği:**
```python
thing_id = 1
response = requests.delete(f"http://localhost:3015/api/v2/twinscale/things/{thing_id}")

if response.status_code == 204:
    print("Thing başarıyla silindi")
```

---

## 🔍 YAML Sorguları

### YAML İçeriğini Arama

TwinScale-Lite, YAML içeriğinde anahtar-değer çiftlerini aramak için güçlü sorgulama özellikleri sunar.

**API Endpoint:** `GET /api/v2/twinscale/things/search`

**Sorgu Parametreleri:**
- `query`: Arama terimi (JSON path veya basit anahtar)
- `value`: Aranacak değer (opsiyonel)

**Örnek 1: Belirli bir sıcaklık değerine sahip tüm sensörler**

```bash
curl "http://localhost:3015/api/v2/twinscale/things/search?query=properties.temperature&value=23.5"
```

**Örnek 2: Belirli bir konumdaki tüm cihazlar**

```bash
curl "http://localhost:3015/api/v2/twinscale/things/search?query=properties.location&value=Office%20Room%20101"
```

**Python ile Karmaşık Sorgulama:**

```python
import requests
import yaml

def search_things_by_property(property_path, value):
    """YAML property path'e göre thing'leri ara"""
    params = {
        "query": property_path,
        "value": value
    }
    response = requests.get(
        "http://localhost:3015/api/v2/twinscale/things/search",
        params=params
    )
    return response.json()

# Sıcaklığı 25°C'den yüksek olan tüm sensörleri bul
all_things = requests.get("http://localhost:3015/api/v2/twinscale/things").json()

hot_sensors = []
for thing in all_things:
    thing_data = yaml.safe_load(thing['yaml_content'])
    temp = thing_data.get('thing', {}).get('properties', {}).get('temperature')
    if temp and temp > 25:
        hot_sensors.append(thing)

print(f"Sıcaklığı 25°C'den yüksek olan {len(hot_sensors)} sensör bulundu")
```

### YAML İçeriğini Python ile İşleme

```python
import yaml
import requests

def get_thing_property(thing_id, property_path):
    """Thing'den belirli bir property'yi al"""
    response = requests.get(f"http://localhost:3015/api/v2/twinscale/things/{thing_id}")
    thing = response.json()

    # YAML parse et
    thing_data = yaml.safe_load(thing['yaml_content'])

    # Property path'i split et ve değeri al
    # Örnek: "properties.temperature" -> ["properties", "temperature"]
    keys = property_path.split('.')
    value = thing_data.get('thing', {})
    for key in keys:
        value = value.get(key)
        if value is None:
            return None

    return value

# Kullanım
temperature = get_thing_property(1, "properties.temperature")
print(f"Sıcaklık: {temperature}°C")
```

---

## 📚 DTDL Kütüphanesi

### Mevcut Arayüzler

#### Base Arayüzler
- **BaseTwin** (`dtmi:twinscale:BaseTwin;1`): Tüm dijital ikizler için temel arayüz
- **SensorTwin** (`dtmi:twinscale:SensorTwin;1`): Sensörler için temel arayüz
- **ActuatorTwin** (`dtmi:twinscale:ActuatorTwin;1`): Aktüatörler için temel arayüz
- **GatewayTwin** (`dtmi:twinscale:GatewayTwin;1`): Ağ geçitleri için temel arayüz

#### Çevresel Sensörler (Environmental)
- **TemperatureSensor** (`dtmi:twinscale:environmental:TemperatureSensor;1`)
- **HumiditySensor** (`dtmi:twinscale:environmental:HumiditySensor;1`)
- **WeatherStation** (`dtmi:twinscale:environmental:WeatherStation;1`)

#### Hava Kalitesi Sensörleri (Air Quality)
- **PM25Sensor** (`dtmi:twinscale:air_quality:PM25Sensor;1`)

#### Sismik Sensörler (Seismic)
- **Building** (`dtmi:twinscale:seismic:Building;1`)
- **Street** (`dtmi:twinscale:seismic:Street;1`)
- **BaseStation** (`dtmi:twinscale:seismic:BaseStation;1`)
- **SeismicSensor** (`dtmi:twinscale:seismic:SeismicSensor;1`)

### Yeni DTDL Arayüzü Ekleme

1. **DTDL JSON dosyasını oluşturun:**

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

2. **Dosyayı uygun dizine kaydedin:**
```
backend/app/dtdl_library/domain/my_domain/MySensor.json
```

3. **registry.json dosyasını güncelleyin:**
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

4. **Backend'i yeniden başlatın:**
```bash
python main.py
```

---

## 📖 API Dokümantasyonu

Backend çalıştığında, interaktif API dokümantasyonuna şu adresten erişebilirsiniz:

- **Swagger UI**: http://localhost:3015/docs
- **ReDoc**: http://localhost:3015/redoc

---

## 🧪 Test

### Test Dosyalarını Çalıştırma

```bash
cd backend

# Tüm testleri çalıştır
pytest tests/

# Belirli bir test dosyasını çalıştır
pytest tests/test_dtdl_loader.py

# Verbose çıktı ile
pytest tests/ -v

# Coverage raporu ile
pytest tests/ --cov=app
```

### Mevcut Testler

- **test_dtdl_loader.py**: DTDL yükleme ve cache işlemleri
- **test_dtdl_converter.py**: DTDL ↔ TwinScale dönüşüm testleri
- **test_dtdl_validator.py**: DTDL doğrulama testleri
- **test_seismic_dtdl.py**: Sismik sensör arayüzleri testleri

### Manuel Test (cURL)

```bash
# Health check
curl http://localhost:3015/health

# DTDL arayüzlerini listele
curl http://localhost:3015/api/v2/dtdl/interfaces

# Belirli bir arayüz detayı
curl "http://localhost:3015/api/v2/dtdl/interfaces/dtmi:twinscale:environmental:TemperatureSensor;1"

# YAML şablonu oluştur
curl -X POST "http://localhost:3015/api/v2/dtdl/convert/to-twinscale" \
  -H "Content-Type: application/json" \
  -d '{"dtmi": "dtmi:twinscale:environmental:TemperatureSensor;1"}'
```

### Docker Container'da Test

```bash
# Backend container'ında testleri çalıştır
docker-compose exec backend pytest tests/ -v

# Container içinde interaktif shell
docker-compose exec backend bash
>>> pytest tests/test_dtdl_loader.py -v
```

---

## 🔧 Sorun Giderme (Troubleshooting)

### Docker ile İlgili Sorunlar

#### Problem: Container'lar başlamıyor

```bash
# Logları kontrol edin
docker-compose logs

# Belirli bir servisin logunu kontrol edin
docker-compose logs backend

# Container'ları temizleyin ve yeniden başlatın
docker-compose down -v
docker-compose up -d --build
```

#### Problem: Port zaten kullanımda

```bash
# Çakışan portları kontrol edin
# Windows:
netstat -ano | findstr :3015
netstat -ano | findstr :3005
netstat -ano | findstr :3030

# Linux/Mac:
lsof -i :3015
lsof -i :3005
lsof -i :3030

# docker-compose.yml dosyasında portları değiştirin
# Örnek: "3016:3015" (host:container)
```

#### Problem: Backend Fuseki'ye bağlanamıyor

```bash
# Fuseki health check
curl http://localhost:3030/$/ping

# Fuseki loglarını kontrol edin
docker-compose logs fuseki

# Network kontrolü
docker network ls
docker network inspect twinscale-network
```

#### Problem: Frontend backend'e erişemiyor

```bash
# nginx.conf dosyasını kontrol edin
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf

# Backend bağlantısını test edin (container içinden)
docker-compose exec frontend curl http://backend:3015/health

# Frontend'i yeniden build edin
docker-compose up -d --build frontend
```

#### Problem: Veriler kayboldu

```bash
# Volume'ları listeleyin
docker volume ls | grep twinscale

# Volume'ları yedekleyin
docker run --rm -v twinscale_fuseki-data:/data -v $(pwd):/backup alpine tar czf /backup/fuseki-backup.tar.gz -C /data .
docker run --rm -v twinscale_backend-data:/data -v $(pwd):/backup alpine tar czf /backup/backend-backup.tar.gz -C /data .

# Volume'ları geri yükleyin
docker run --rm -v twinscale_fuseki-data:/data -v $(pwd):/backup alpine tar xzf /backup/fuseki-backup.tar.gz -C /data
```

### Genel Sorunlar

#### Problem: DTDL arayüzü yüklenmiyor

```bash
# Registry dosyasını kontrol edin
cat backend/app/dtdl_library/registry.json

# DTDL dosyasının varlığını kontrol edin
ls -la backend/app/dtdl_library/domain/

# Backend loglarını kontrol edin
docker-compose logs backend | grep -i dtdl
# veya manuel:
tail -f backend/logs/app.log
```

#### Problem: YAML parse hatası

```python
# YAML formatını doğrulayın
import yaml

yaml_content = """
thing:
  name: MyThing
  interface: TemperatureSensor
"""

try:
    data = yaml.safe_load(yaml_content)
    print("YAML geçerli:", data)
except yaml.YAMLError as e:
    print("YAML hatası:", e)
```

#### Problem: CORS hatası

```bash
# Backend .env dosyasını kontrol edin
grep CORS backend/.env

# docker-compose.yml'de CORS ayarlarını kontrol edin
grep -A 5 CORS docker-compose.yml

# CORS_ORIGINS ortam değişkenini güncelleyin
CORS_ORIGINS=http://localhost,http://localhost:3005,http://localhost:5173
```

### Performance İpuçları

```bash
# Docker container resource kullanımı
docker stats

# Backend memory kullanımı
docker-compose exec backend ps aux

# Fuseki JVM memory ayarı
# docker-compose.yml içinde:
# JVM_ARGS=-Xmx2g  # 2GB'den fazla RAM varsa artırın

# Log boyutunu sınırlayın
docker-compose logs --tail=100 backend
```

---

## 📁 Proje Yapısı

```
thing-for-twinscale/
├── backend/                      # Python/FastAPI backend
│   ├── app/
│   │   ├── api/                  # API endpoints
│   │   │   └── v2/
│   │   │       ├── dtdl.py       # DTDL API
│   │   │       └── twinscale.py  # TwinScale API
│   │   ├── core/                 # Temel yapılandırma
│   │   │   ├── config.py         # Ayarlar
│   │   │   └── database.py       # Veritabanı
│   │   ├── dtdl_library/         # DTDL arayüz kütüphanesi
│   │   │   ├── base/             # Temel arayüzler
│   │   │   │   ├── BaseTwin.json
│   │   │   │   ├── SensorTwin.json
│   │   │   │   ├── ActuatorTwin.json
│   │   │   │   └── GatewayTwin.json
│   │   │   ├── domain/           # Alan-spesifik arayüzler
│   │   │   │   ├── environmental/
│   │   │   │   │   ├── TemperatureSensor.json
│   │   │   │   │   ├── HumiditySensor.json
│   │   │   │   │   └── WeatherStation.json
│   │   │   │   ├── air_quality/
│   │   │   │   │   └── PM25Sensor.json
│   │   │   │   └── seismic/
│   │   │   │       ├── Building.json
│   │   │   │       ├── Street.json
│   │   │   │       ├── BaseStation.json
│   │   │   │       └── SeismicSensor.json
│   │   │   └── registry.json     # Arayüz kayıt defteri
│   │   ├── models/               # SQLAlchemy ORM modelleri
│   │   ├── schemas/              # Pydantic şemaları
│   │   └── services/             # İş mantığı servisleri
│   │       ├── dtdl_loader_service.py      # DTDL yükleme
│   │       ├── dtdl_converter_service.py   # DTDL dönüşüm
│   │       └── dtdl_validator_service.py   # DTDL doğrulama
│   ├── tests/                    # Test dosyaları
│   │   ├── test_dtdl_loader.py
│   │   ├── test_dtdl_converter.py
│   │   ├── test_dtdl_validator.py
│   │   └── test_seismic_dtdl.py
│   ├── main.py                   # Uygulama giriş noktası
│   ├── requirements.txt          # Python bağımlılıkları
│   ├── Dockerfile                # Backend Docker image
│   ├── .dockerignore             # Docker ignore dosyası
│   └── .env.example              # Ortam değişkenleri örneği
│
├── frontend/                     # React/Vite frontend
│   ├── src/
│   │   ├── api/                  # API istemcileri
│   │   │   ├── dtdl.js           # DTDL API
│   │   │   └── twinscale.js      # TwinScale API
│   │   ├── components/           # React bileşenleri
│   │   │   └── dtdl/             # DTDL UI bileşenleri
│   │   │       ├── DTDLSelectionModal.jsx
│   │   │       └── DTDLValidationPanel.jsx
│   │   ├── pages/                # Sayfa bileşenleri
│   │   │   └── twinscale/        # TwinScale sayfaları
│   │   │       ├── CreateTwinScaleThing.jsx
│   │   │       └── TwinScaleThingDetails.jsx
│   │   └── locales/              # i18n çevirileri
│   │       ├── en/
│   │       └── tr/
│   ├── package.json              # Node bağımlılıkları
│   ├── vite.config.js            # Vite yapılandırması
│   ├── Dockerfile                # Frontend Docker image (multi-stage)
│   ├── nginx.conf                # Nginx yapılandırması
│   └── .dockerignore             # Docker ignore dosyası
│
├── docker-compose.yml            # Docker Compose yapılandırması
└── README.md                     # Bu dosya
```

### Docker Servisleri

Docker Compose ile 3 servis ayağa kaldırılır:

1. **fuseki** (Port 3030): Apache Jena Fuseki RDF Triple Store
   - SPARQL endpoint
   - RDF veri saklama
   - 2GB JVM heap memory

2. **backend** (Port 3015): FastAPI backend
   - REST API
   - DTDL yönetimi
   - TwinScale YAML işleme
   - SQLite veritabanı

3. **frontend** (Port 3005): React + Nginx
   - SPA web arayüzü
   - Nginx reverse proxy
   - Gzip compression
   - Static asset caching

---

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen:

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

---

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

---

## 📧 İletişim

Sorularınız için lütfen bir issue açın veya [e-posta gönderin](mailto:your-email@example.com).

---

## 🙏 Teşekkürler

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI kütüphanesi
- [DTDL](https://github.com/Azure/opendigitaltwins-dtdl) - Digital Twins Definition Language
