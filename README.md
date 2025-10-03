# CNC Machine Data Streaming Infrastructure 🏭

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?style=for-the-badge&logo=apache-kafka&logoColor=white)](https://kafka.apache.org)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![TimescaleDB](https://img.shields.io/badge/TimescaleDB-FDB515?style=for-the-badge&logo=timescale&logoColor=white)](https://timescale.com)
[![OPC UA](https://img.shields.io/badge/OPC%20UA-62B1D0?style=for-the-badge&logo=opc-foundation&logoColor=white)](https://opcfoundation.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://tensorflow.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![Dash](https://img.shields.io/badge/Dash-008DE4?style=for-the-badge&logo=plotly&logoColor=white)](https://dash.plotly.com)
[![YOLO](https://img.shields.io/badge/YOLO-00FFFF?style=for-the-badge&logo=yolo&logoColor=black)](https://ultralytics.com)
[![Faust](https://img.shields.io/badge/Faust-FF6B6B?style=for-the-badge&logo=python&logoColor=white)](https://faust.readthedocs.io)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://sqlalchemy.org)
[![Alembic](https://img.shields.io/badge/Alembic-FF6B6B?style=for-the-badge&logo=python&logoColor=white)](https://alembic.sqlalchemy.org)

A real-time data streaming infrastructure designed for CNC machine monitoring and AI-powered analysis. This system enables continuous data acquisition, processing, and anomaly detection for industrial manufacturing environments.

## 🎯 Motivation

The motivation for designing and developing a data streaming infrastructure for an AI laboratory is to enable near-real-time data processing and analysis for various AI applications and experiments. Data streaming allows for continuous data acquisition and processing, thereby improving the performance and reliability of AI models. AI models can learn from new data and events, thus improving their accuracy. Additionally, AI models can detect anomalies in near real-time through data streaming.

## 📋 Project Objectives

The primary goals of this project include:

1. **Design and develop a data streaming pipeline** using OPC UA Server for sensor data reading and Apache Kafka as data integration system
2. **Research and implement** data flow processing and storage, particularly for image data and time series data
3. **Create predictions** from preprocessed data using pre-trained AI models
4. **Test and validate** the functionality of the data streaming pipeline

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CNC Machine   │    │  OPC UA      │    │  Apache Kafka   │    │  AI Processing  │
│   Sensors       │───▶│  Server      │───▶│  Cluster        │───▶│  & Analytics  │
│                 │    │              │    │                 │    │                 │
└─────────────────┘    └──────────────┘    └─────────────────┘    └─────────────────┘
                                                                           │
                                                    ▼
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐             │
│   Web Dashboard │    │  TimescaleDB │    │  Faust Stream   │
│   (Plotly/Dash) │◀───│  PostgreSQL  │◀───│  Processing    │ ◀──────    │ 
│                 │    │              │    │                 │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

## 🚀 Features

- **Real-time Data Streaming**: Continuous acquisition of sensor data from CNC machines
- **Multi-Modal Data Processing**: Handles both time series and image data streams
- **AI-Powered Analytics**: 
  - LSTM Autoencoder for anomaly detection
  - YOLO-based computer vision for image analysis
  - Real-time prediction capabilities
- **Scalable Infrastructure**: Docker-based microservices architecture
- **Interactive Dashboard**: Real-time visualization with Plotly and Dash
- **Data Persistence**: TimescaleDB for efficient time series storage
- **Stream Processing**: Faust-based real-time data processing

## 🛠️ Technology Stack

### Core Technologies
- **Python 3.10+**: Primary programming language
- **Apache Kafka**: Distributed streaming platform
- **OPC UA**: Industrial communication protocol
- **Docker & Docker Compose**: Containerization and orchestration

### Data Storage
- **PostgreSQL**: Primary database
- **TimescaleDB**: Time series database extension
- **SQLAlchemy**: ORM and database toolkit
- **Alembic**: Database migration tool

### AI/ML Frameworks
- **PyTorch**: Deep learning framework for LSTM autoencoder
- **TensorFlow**: Machine learning platform
- **Ultralytics YOLO**: Computer vision model
- **Scikit-learn**: Machine learning utilities

### Stream Processing
- **Faust**: Stream processing library
- **Confluent Kafka**: Enterprise Kafka client
- **Kafka-Python**: Python Kafka client

### Visualization & UI
- **Plotly**: Interactive plotting library
- **Dash**: Web application framework
- **Pandas**: Data manipulation and analysis

### Image Processing
- **OpenCV**: Computer vision library
- **Pillow (PIL)**: Image processing library

```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.10+
- Pipenv (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/daten-streaming-infrastruktur.git
   cd daten-streaming-infrastruktur
   ```

2. **Install Python dependencies**
   ```bash
   pipenv install
   pipenv shell
   ```

3. **Start the infrastructure services**
   ```bash
   docker-compose up -d
   ```

4. **Initialize the database**
   ```bash
   python emptydb.py
   pipenv run apply_migrations
   ```

5. **Insert demo data** (optional)
   ```bash
   python insert_demo_data.py
   ```

### Running the Application

1. **Start the OPC UA Server**
   ```bash
   cd OPCUA
   python Main.py
   ```

2. **Launch Kafka consumers**
   ```bash
   python Kafka_Test/kafka_consumer_timeseries.py
   python Kafka_Test/kafka_consumer_image.py
   ```

3. **Start Faust stream processing**
   ```bash
   python -m Faust.faust_test_timeseries worker --loglevel=info
   python -m Faust.faust_test_image worker --loglevel=info
   ```

4. **Launch the web dashboard**
   ```bash
   python ui_plotly.py
   ```

   Access the dashboard at `http://localhost:8050`

## 🔧 Configuration

Edit `config.yml` to customize:

- **OPC UA Settings**: Server endpoint and node configuration
- **Kafka Configuration**: Bootstrap servers, topics, and producer settings
- **Data Sources**: File paths for demo time series and image data

## 📊 Data Flow

1. **Data Acquisition**: OPC UA server reads sensor data from CNC machines
2. **Message Queuing**: Data streams through Apache Kafka topics
3. **Stream Processing**: Faust applications process data in real-time
4. **AI Analysis**: LSTM autoencoders detect anomalies in time series data
5. **Data Storage**: Processed data stored in TimescaleDB
6. **Visualization**: Real-time dashboard displays metrics and alerts

## 🤖 AI Models

### LSTM Autoencoder
- **Purpose**: Anomaly detection in time series sensor data
- **Architecture**: Encoder-Decoder with LSTM layers
- **Features**: Real-time anomaly scoring and threshold-based alerting

### Computer Vision
- **YOLO Integration**: Object detection and classification in CNC machine images
- **Image Processing**: Real-time analysis of manufacturing processes

## 📈 Monitoring & Visualization

The web dashboard provides:
- Real-time sensor data visualization
- Anomaly detection alerts
- Historical data analysis
- Image stream monitoring
- System health metrics

## 🧪 Testing

Run the test suite:
```bash
python test_func_database.py
python test_orm.py
```



## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Relevant Documentation

- [Migration tool (Alembic)](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [SQL ORM (SQLAlchemy)](https://docs.sqlalchemy.org/en/20/tutorial/index.html)
- [OPC UA Python](https://python-opcua.readthedocs.io/en/latest/)
- [Apache Kafka](https://hub.docker.com/r/confluentinc/cp-kafka/)
- [Faust Streaming](https://faust.readthedocs.io/en/latest/)
- [TimescaleDB](https://docs.timescale.com/)

---

**Built with ❤️ for Industrial IoT and Smart Manufacturing**
