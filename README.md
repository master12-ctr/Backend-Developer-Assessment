# 🚀 IDEEZA Analytics API - Senior Backend Developer Assessment

## 📋 Project Overview
A production-ready Django analytics system with three comprehensive REST APIs for blog view analytics. This solution demonstrates senior-level backend development skills with complete implementation of all assessment requirements plus advanced enterprise features.

## ✅ All Assessment Requirements Met

### **API #1 — `/analytics/blog-views/`**
- ✅ `object_type = country/user` - Group blogs and views by selected object_type
- ✅ `Range: month/week/year` - Time range filtering  
- ✅ `x = grouping key, y = number_of_blogs, z = total views` - Consistent output structure
- ✅ **Dynamic filters** (and/or/not/eq) - Advanced multi-table filtering
- ✅ **Pagination** - Limit/offset pagination for large datasets
- ✅ **Optimized queries** - Efficient Django ORM with strategic indexing

### **API #2 — `/analytics/top/`**
- ✅ `top = user/country/blog` - Top 10 based on total views
- ✅ `x, y, z vary depending on selected top type` - Flexible output format
- ✅ **Time range support** - Filter by month/week/year
- ✅ **Dynamic filters** - Complex filtering capabilities
- ✅ **Performance optimized** - Efficient queries with database indexes

### **API #3 — `/analytics/performance/`**
- ✅ `compare = month/week/day/year` - Time-series performance analysis
- ✅ `x = period label + number_of_blogs created` - Comprehensive period labeling
- ✅ `y = views during the period` - View count aggregation
- ✅ `z = growth/decline percentage vs previous period` - Growth calculation
- ✅ **User-specific or all users** - Flexible user filtering
- ✅ **Dynamic filtering** - Advanced filter support

### **General Requirements**
- ✅ **Efficient Django ORM** - Optimized queries with `select_related`, proper indexing
- ✅ **Dynamic multi-table filtering** - Complex JSON-based filter system
- ✅ **Time-series aggregation and comparison** - Advanced period-based analysis
- ✅ **N+1 query prevention** - Strategic use of `select_related` and `prefetch_related`
- ✅ **Consistent x, y, z output structure** - All APIs follow the same pattern

## 🏆 Advanced Features Implemented

### **Production Readiness**
- 📊 **Comprehensive Monitoring** - API request logging, performance metrics, error tracking
- 🛡️ **Enterprise Error Handling** - Custom exceptions with proper logging and user feedback
- 📈 **Performance Optimization** - Database indexes, query optimization, pagination
- 🔍 **API Documentation** - Swagger/OpenAPI with interactive testing
- 📱 **RESTful Design** - Proper HTTP methods, status codes, and response formats

### **Developer Experience**
- 🧪 **Complete Test Suite** - Unit tests, integration tests, performance tests
- ⚡ **Performance Testing** - Built-in performance benchmarking tool
- 🔧 **Management Commands** - Sample data population, database utilities
- 📚 **Comprehensive Documentation** - API docs, setup instructions, examples
- 🎯 **Code Quality** - PEP 8 compliance, proper project structure

## 🚀 Quick Start

### **Prerequisites**
- Python 3.11+
- SQLite (default) or PostgreSQL
- Virtual environment (recommended)

### **Installation**

```bash
# 1. Clone the repository
git clone <repository-url>
cd ideeza_assessment

# 2. Create and activate virtual environment
python -m venv env
source env/bin/activate  # Linux/Mac
# OR
env\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env file with your database settings

# 5. Run database migrations
python manage.py migrate

# 6. Create superuser (optional)
python manage.py createsuperuser

# 7. Load sample data
python manage.py load_sample_data

# 8. Run development server
python manage.py runserver


Access URLs
🌐 API Documentation: http://localhost:8000/swagger/

📖 ReDoc Documentation: http://localhost:8000/redoc/

🔧 Admin Panel: http://localhost:8000/admin/