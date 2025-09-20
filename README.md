# Airline Experience Analytics Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

## 🎯 Overview

A comprehensive analytics dashboard for airline customer experience analysis, built with Streamlit. This dashboard provides insights into:

- **Customer Satisfaction Drivers** - What makes passengers happy vs frustrated
- **Review Theme Analysis** - Hidden pain points and success patterns  
- **Competitive Landscape** - Performance across airlines, routes, and regions
- **Segment Analysis** - Satisfaction by class, traveler type, and geography

## ✨ Key Features

### 📊 Interactive Analytics
- Real-time filtering by airline, seat class, traveler type, and rating range
- Dynamic visualizations that update based on selections
- Comprehensive satisfaction metrics and KPIs

### 🎨 Rich Visualizations
- Performance matrices and competitive analysis
- Geographic route performance mapping
- Service correlation analysis
- Satisfaction segment distributions

### 💡 Business Insights
- Automated insight generation
- Pain point detection from review themes
- Service gap analysis between passenger segments
- Competitive positioning analytics

## 🚀 Live Demo

**Dashboard URL:** [https://your-dashboard.streamlit.app](https://your-dashboard.streamlit.app)

## 📁 Project Structure

```
airline-dashboard/
├── advanced_airline_dashboard.py    # Main dashboard application
├── requirements.txt                 # Python dependencies
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── Airline Review.csv              # Dataset (23K+ reviews)
├── deployment_guide.md             # Deployment instructions
└── README.md                       # This file
```

## 🛠️ Local Development

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/airline-dashboard.git
   cd airline-dashboard
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard:**
   ```bash
   streamlit run advanced_airline_dashboard.py
   ```

4. **Open in browser:**
   - Local URL: `http://localhost:8501`

## 📊 Dataset

The dashboard analyzes airline reviews containing:
- **23,171 reviews** across multiple airlines
- **Service ratings** (seat comfort, staff service, food, etc.)
- **Route information** (origin, destination, connections)
- **Passenger demographics** (traveler type, seat class)
- **Overall satisfaction** and recommendation data

## 🎨 Dashboard Sections

### 1. Satisfaction Overview
- Key performance metrics and trends
- Rating distribution analysis
- Customer satisfaction segments

### 2. Happiness vs Frustration Drivers
- Service correlation analysis
- Happy vs frustrated passenger comparison
- Service gap identification

### 3. Review Themes & Pain Points
- Automated theme extraction
- Common pain point analysis
- Success pattern identification

### 4. Competitive Landscape
- Airline performance ranking
- Market position analysis
- Performance gaps and opportunities

### 5. Geographic Performance
- Route-level satisfaction analysis
- Origin/destination performance
- Regional insights

### 6. Segment Analysis
- Performance by seat class
- Traveler type analysis
- Premium vs economy gaps

## 🔧 Technical Stack

- **Framework:** Streamlit
- **Data Processing:** Pandas, NumPy
- **Visualizations:** Plotly, Matplotlib, Seaborn
- **Analytics:** Scikit-learn, SciPy
- **Deployment:** Streamlit Community Cloud

## 📈 Key Insights

The dashboard reveals critical insights including:
- **Service Quality** is the top satisfaction driver
- **Communication gaps** are major pain points
- **Premium class** shows 2.1 point satisfaction advantage
- **Route performance** varies significantly by geography
- **Hidden themes** in negative reviews reveal improvement opportunities

## 🚀 Deployment

### Streamlit Community Cloud (Recommended)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Deploy airline dashboard"
   git push origin main
   ```

2. **Deploy on Streamlit:**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select `advanced_airline_dashboard.py`
   - Deploy!

3. **Your dashboard will be live at:**
   ```
   https://YOUR_USERNAME-airline-dashboard-advanced-airline-dashboard-xyz.streamlit.app
   ```

### Alternative Platforms
- **Heroku:** Free tier available
- **Railway:** Modern deployment platform
- **Render:** Simple and reliable

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or feedback, please open an issue or contact [your-email@example.com](mailto:your-email@example.com).

---

**Built with ❤️ using Streamlit • Powering data-driven airline insights**