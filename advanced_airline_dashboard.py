import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Try to import advanced NLP components (optional)
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.util import ngrams
    from collections import Counter
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Airline Experience Analytics Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .section-header {
        font-size: 2rem;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #ff7f0e;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #1f77b4;
        margin: 1rem 0;
    }
    .pain-point {
        background-color: #ffe6e6;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 3px solid #ff4444;
        margin: 0.5rem 0;
    }
    .success-point {
        background-color: #e6ffe6;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 3px solid #44ff44;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_process_data():
    """Load and process the airline review data"""
    try:
        # Load the main dataset
        df = pd.read_csv('Airline Review.csv', index_col=0)
        
        # Parse routes into origin, destination, via
        def parse_route(route_str):
            if pd.isna(route_str):
                return None, None, None
            
            route_str = str(route_str).strip()
            
            if " via " in route_str.lower():
                main_route, via_part = route_str.split(" via ", 1)
                via_city = via_part.strip()
                
                if " to " in main_route.lower():
                    origin, destination = main_route.split(" to ", 1)
                    return origin.strip(), destination.strip(), via_city
                else:
                    return route_str, None, None
            
            elif " to " in route_str.lower():
                parts = route_str.split(" to ", 1)
                if len(parts) == 2:
                    return parts[0].strip(), parts[1].strip(), None
                else:
                    return route_str, None, None
            else:
                return route_str, None, None
        
        # Apply route parsing
        route_data = df['Route'].apply(parse_route)
        df['Origin'] = [x[0] for x in route_data]
        df['Destination'] = [x[1] for x in route_data]
        df['Via'] = [x[2] for x in route_data]
        
        # Create satisfaction segments
        def categorize_satisfaction(rating):
            if rating >= 8:
                return 'Happy (8-10)'
            elif rating >= 6:
                return 'Neutral (6-7)'
            elif rating >= 3:
                return 'Disappointed (3-5)'
            else:
                return 'Very Disappointed (1-2)'
        
        df['Satisfaction_Segment'] = df['Overall_Rating'].apply(categorize_satisfaction)
        
        # Define service columns
        service_cols = ['Seat Comfort', 'Cabin Staff Service', 'Food & Beverages', 
                       'Ground Service', 'Inflight Entertainment', 'Wifi & Connectivity', 
                       'Value For Money']
        
        # Add review length
        df['Review_Length'] = df['Review'].fillna('').astype(str).str.len()
        
        return df, service_cols
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

def extract_review_themes(df, sentiment='positive'):
    """Extract themes from reviews using simple keyword analysis"""
    if sentiment == 'positive':
        reviews = df[df['Overall_Rating'] >= 8]['Review'].fillna('')
    else:
        reviews = df[df['Overall_Rating'] <= 3]['Review'].fillna('')
    
    # Combine all reviews
    all_text = ' '.join(reviews.astype(str)).lower()
    
    # Define theme keywords
    positive_themes = {
        'Staff Service': ['crew', 'staff', 'service', 'friendly', 'helpful', 'professional'],
        'Comfort': ['comfortable', 'seat', 'legroom', 'spacious', 'clean'],
        'Food & Beverage': ['food', 'meal', 'drink', 'beverage', 'delicious', 'tasty'],
        'Efficiency': ['on time', 'punctual', 'quick', 'fast', 'efficient'],
        'Value': ['value', 'price', 'cheap', 'reasonable', 'worth'],
        'Entertainment': ['entertainment', 'movie', 'tv', 'screen', 'wifi'],
        'Airport Experience': ['check-in', 'boarding', 'airport', 'lounge', 'gate']
    }
    
    negative_themes = {
        'Poor Service': ['poor service', 'rude', 'unprofessional', 'slow service', 'bad service'],
        'Delays': ['delay', 'late', 'cancelled', 'postponed', 'waiting'],
        'Discomfort': ['uncomfortable', 'cramped', 'dirty', 'broken', 'small seat'],
        'Food Issues': ['bad food', 'poor meal', 'no food', 'terrible food', 'cold food'],
        'Booking Problems': ['booking', 'reservation', 'website', 'customer service'],
        'Baggage Issues': ['baggage', 'luggage', 'lost', 'damaged', 'extra charge'],
        'Communication': ['information', 'communication', 'announcement', 'language barrier']
    }
    
    themes = positive_themes if sentiment == 'positive' else negative_themes
    theme_counts = {}
    
    for theme, keywords in themes.items():
        count = sum(all_text.count(keyword) for keyword in keywords)
        theme_counts[theme] = count
    
    return sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)

def create_satisfaction_overview(df, service_cols):
    """Create satisfaction overview metrics and charts"""
    st.markdown('<div class="section-header">📊 Flight Experience Satisfaction Overview</div>', unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        avg_satisfaction = df['Overall_Rating'].mean()
        st.metric("Average Satisfaction", f"{avg_satisfaction:.2f}/10", 
                 delta=f"{(avg_satisfaction-5):.1f} vs neutral")
        
    with col2:
        happy_rate = (df['Overall_Rating'] >= 8).mean() * 100
        st.metric("Happy Customers", f"{happy_rate:.1f}%")
        
    with col3:
        recommendation_rate = (df['Recommended'] == 'yes').mean() * 100
        st.metric("Recommendation Rate", f"{recommendation_rate:.1f}%")
        
    with col4:
        service_quality = df[service_cols].mean().mean()
        st.metric("Service Quality", f"{service_quality:.2f}/5")
        
    with col5:
        total_reviews = len(df)
        st.metric("Total Reviews", f"{total_reviews:,}")
    
    # Satisfaction distribution and trends
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(df, x='Overall_Rating', nbins=10, 
                          title="Overall Rating Distribution",
                          color_discrete_sequence=['#1f77b4'])
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        segment_dist = df['Satisfaction_Segment'].value_counts()
        fig = px.pie(values=segment_dist.values, names=segment_dist.index,
                    title="Satisfaction Segments",
                    color_discrete_sequence=['#ff4444', '#ff8800', '#88ccff', '#44ff44'])
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

def analyze_happiness_drivers(df, service_cols):
    """Analyze what makes passengers happiest or most frustrated"""
    st.markdown('<div class="section-header">😊 What Makes Passengers Happy vs Frustrated</div>', unsafe_allow_html=True)
    
    # Service correlation analysis
    correlations = []
    for col in service_cols:
        corr = df[col].corr(df['Overall_Rating'])
        correlations.append({'Service': col, 'Correlation': corr})
    
    corr_df = pd.DataFrame(correlations).sort_values('Correlation', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(corr_df, x='Correlation', y='Service', orientation='h',
                    title="Service Aspects vs Overall Satisfaction",
                    color='Correlation', color_continuous_scale='RdYlGn')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Key insights
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.write("**🎯 Key Happiness Drivers:**")
        for i, row in corr_df.head(3).iterrows():
            st.write(f"• **{row['Service']}**: {row['Correlation']:.3f} correlation")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Compare happy vs frustrated passengers
        happy_passengers = df[df['Overall_Rating'] >= 8]
        frustrated_passengers = df[df['Overall_Rating'] <= 3]
        
        happy_means = happy_passengers[service_cols].mean()
        frustrated_means = frustrated_passengers[service_cols].mean()
        
        comparison_df = pd.DataFrame({
            'Happy Passengers': happy_means,
            'Frustrated Passengers': frustrated_means,
            'Service Aspect': service_cols
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Happy Passengers', x=comparison_df['Service Aspect'], 
                            y=comparison_df['Happy Passengers'], marker_color='lightgreen'))
        fig.add_trace(go.Bar(name='Frustrated Passengers', x=comparison_df['Service Aspect'], 
                            y=comparison_df['Frustrated Passengers'], marker_color='lightcoral'))
        
        fig.update_layout(title="Service Ratings: Happy vs Frustrated Passengers",
                         xaxis_title="Service Aspect", yaxis_title="Average Rating",
                         barmode='group', height=400)
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Service gaps
        service_gaps = happy_means - frustrated_means
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.write("**📈 Biggest Service Gaps:**")
        for service, gap in service_gaps.nlargest(3).items():
            st.write(f"• **{service}**: {gap:.2f} point difference")
        st.markdown('</div>', unsafe_allow_html=True)

def analyze_review_themes_advanced(df):
    """Advanced analysis of recurring themes in reviews"""
    st.markdown('<div class="section-header">💬 Review Themes & Hidden Pain Points</div>', unsafe_allow_html=True)
    
    # Extract themes
    positive_themes = extract_review_themes(df, 'positive')
    negative_themes = extract_review_themes(df, 'negative')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎉 What Makes Passengers Happy")
        
        # Display positive themes
        for i, (theme, count) in enumerate(positive_themes[:6], 1):
            st.markdown(f'<div class="success-point">{i}. <strong>{theme}</strong> ({count} mentions)</div>', 
                       unsafe_allow_html=True)
        
        # Positive insights
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.write("**✨ Success Patterns:**")
        st.write("• Staff service excellence drives satisfaction")
        st.write("• Comfort is a key differentiator")
        st.write("• Efficiency creates positive experiences")
        st.markdown('</div>', unsafe_allow_html=True)
            
    with col2:
        st.subheader("😞 Common Pain Points")
        
        # Display negative themes
        for i, (theme, count) in enumerate(negative_themes[:6], 1):
            st.markdown(f'<div class="pain-point">{i}. <strong>{theme}</strong> ({count} mentions)</div>', 
                       unsafe_allow_html=True)
        
        # Pain point insights
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.write("**⚠️ Hidden Pain Points:**")
        st.write("• Service quality inconsistency")
        st.write("• Communication breakdowns")
        st.write("• Operational delays impact perception")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Review patterns analysis
    st.subheader("📝 Review Pattern Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Review length by satisfaction
        review_stats = df.groupby('Satisfaction_Segment').agg({
            'Review_Length': ['mean', 'count'],
            'Overall_Rating': 'mean'
        }).round(2)
        review_stats.columns = ['Avg_Length', 'Count', 'Avg_Rating']
        
        fig = px.bar(x=review_stats.index, y=review_stats['Avg_Length'],
                    title="Average Review Length by Satisfaction",
                    color=review_stats['Avg_Rating'], color_continuous_scale='RdYlGn')
        fig.update_layout(xaxis_title="Satisfaction Segment", 
                         yaxis_title="Average Review Length (characters)")
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # Recommendation patterns
        rec_by_segment = df.groupby('Satisfaction_Segment').apply(
            lambda x: (x['Recommended'] == 'yes').mean() * 100
        )
        
        fig = px.bar(x=rec_by_segment.index, y=rec_by_segment.values,
                    title="Recommendation Rate by Satisfaction Segment",
                    color=rec_by_segment.values, color_continuous_scale='RdYlGn')
        fig.update_layout(xaxis_title="Satisfaction Segment", 
                         yaxis_title="Recommendation Rate (%)")
        st.plotly_chart(fig, use_container_width=True)

def analyze_competitive_landscape(df):
    """Comprehensive competitive analysis"""
    st.markdown('<div class="section-header">🏆 Competitive Landscape Analysis</div>', unsafe_allow_html=True)
    
    # Airline performance metrics
    airline_metrics = df.groupby('Airline Name').agg({
        'Overall_Rating': ['mean', 'count'],
        'Recommended': lambda x: (x == 'yes').mean() * 100
    }).round(2)
    airline_metrics.columns = ['Avg_Rating', 'Review_Count', 'Recommendation_Rate']
    airline_metrics = airline_metrics[airline_metrics['Review_Count'] >= 10]
    airline_metrics = airline_metrics.sort_values('Avg_Rating', ascending=False)
    
    # Performance quadrant analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Top performers
        top_airlines = airline_metrics.head(15)
        fig = px.bar(x=top_airlines['Avg_Rating'], y=top_airlines.index, orientation='h',
                    title="Top 15 Airlines by Average Rating",
                    color=top_airlines['Avg_Rating'], color_continuous_scale='RdYlGn')
        fig.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # Performance matrix: Rating vs Recommendation
        fig = px.scatter(airline_metrics, x='Avg_Rating', y='Recommendation_Rate',
                        size='Review_Count', hover_name=airline_metrics.index,
                        title="Performance Matrix: Rating vs Recommendations",
                        color='Avg_Rating', color_continuous_scale='RdYlGn')
        
        # Add quadrant lines
        median_rating = airline_metrics['Avg_Rating'].median()
        median_rec = airline_metrics['Recommendation_Rate'].median()
        fig.add_hline(y=median_rec, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=median_rating, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    # Competitive insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.write("**🥇 Top Performers:**")
        best_airline = airline_metrics.iloc[0]
        highest_rec = airline_metrics.loc[airline_metrics['Recommendation_Rate'].idxmax()]
        st.write(f"• Best Rating: **{best_airline.name}** ({best_airline['Avg_Rating']:.2f}/10)")
        st.write(f"• Highest Recommendations: **{highest_rec.name}** ({highest_rec['Recommendation_Rate']:.1f}%)")
        st.write(f"• Market Leaders show consistency across metrics")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.write("**📊 Market Analysis:**")
        performance_gap = airline_metrics['Avg_Rating'].max() - airline_metrics['Avg_Rating'].min()
        high_performers = (airline_metrics['Avg_Rating'] >= airline_metrics['Avg_Rating'].quantile(0.8)).sum()
        st.write(f"• Performance Gap: **{performance_gap:.2f}** points")
        st.write(f"• High Performers: **{high_performers}** airlines (top 20%)")
        st.write(f"• Clear differentiation opportunities exist")
        st.markdown('</div>', unsafe_allow_html=True)

def analyze_geographic_performance(df):
    """Enhanced geographic and route analysis"""
    st.markdown('<div class="section-header">🌍 Geographic Performance & Route Analysis</div>', unsafe_allow_html=True)
    
    # Route performance analysis
    route_performance = df.groupby('Route').agg({
        'Overall_Rating': ['mean', 'count'],
        'Recommended': lambda x: (x == 'yes').mean() * 100
    }).round(2)
    route_performance.columns = ['Avg_Rating', 'Review_Count', 'Recommendation_Rate']
    route_performance = route_performance[route_performance['Review_Count'] >= 5]
    route_performance = route_performance.sort_values('Avg_Rating', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Best routes
        top_routes = route_performance.head(12)
        fig = px.bar(x=top_routes['Avg_Rating'], y=top_routes.index, orientation='h',
                    title="Top Routes by Satisfaction",
                    color=top_routes['Avg_Rating'], color_continuous_scale='RdYlGn')
        fig.update_layout(showlegend=False, height=450)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # Challenging routes
        bottom_routes = route_performance.tail(12)
        fig = px.bar(x=bottom_routes['Avg_Rating'], y=bottom_routes.index, orientation='h',
                    title="Most Challenging Routes",
                    color=bottom_routes['Avg_Rating'], color_continuous_scale='Reds_r')
        fig.update_layout(showlegend=False, height=450)
        st.plotly_chart(fig, use_container_width=True)
    
    # Geographic insights
    col1, col2 = st.columns(2)
    
    with col1:
        # Origin performance
        origin_performance = df.groupby('Origin')['Overall_Rating'].agg(['mean', 'count'])
        origin_performance = origin_performance[origin_performance['count'] >= 10]
        origin_performance = origin_performance.sort_values('mean', ascending=False).head(10)
        
        fig = px.bar(x=origin_performance['mean'], y=origin_performance.index, orientation='h',
                    title="Top Origin Cities by Satisfaction",
                    color=origin_performance['mean'], color_continuous_scale='Greens')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # Destination performance
        dest_performance = df.groupby('Destination')['Overall_Rating'].agg(['mean', 'count'])
        dest_performance = dest_performance[dest_performance['count'] >= 10]
        dest_performance = dest_performance.sort_values('mean', ascending=False).head(10)
        
        fig = px.bar(x=dest_performance['mean'], y=dest_performance.index, orientation='h',
                    title="Top Destination Cities by Satisfaction",
                    color=dest_performance['mean'], color_continuous_scale='Blues')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

def analyze_class_and_traveler_segments(df):
    """Analyze satisfaction by class and traveler type"""
    st.markdown('<div class="section-header">👥 Class & Traveler Segment Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Class performance
        class_performance = df.groupby('Seat Type').agg({
            'Overall_Rating': 'mean',
            'Recommended': lambda x: (x == 'yes').mean() * 100
        }).round(2)
        class_performance.columns = ['Avg_Rating', 'Recommendation_Rate']
        class_performance = class_performance.sort_values('Avg_Rating', ascending=False)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Average Rating', x=class_performance.index, 
                            y=class_performance['Avg_Rating'], marker_color='skyblue'))
        
        fig.update_layout(title="Performance by Seat Class",
                         xaxis_title="Seat Class", yaxis_title="Average Rating",
                         height=400)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # Traveler type performance
        traveler_performance = df.groupby('Type Of Traveller').agg({
            'Overall_Rating': 'mean',
            'Recommended': lambda x: (x == 'yes').mean() * 100
        }).round(2)
        traveler_performance.columns = ['Avg_Rating', 'Recommendation_Rate']
        traveler_performance = traveler_performance.sort_values('Avg_Rating', ascending=False)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Average Rating', x=traveler_performance.index, 
                            y=traveler_performance['Avg_Rating'], marker_color='lightcoral'))
        
        fig.update_layout(title="Performance by Traveler Type",
                         xaxis_title="Traveler Type", yaxis_title="Average Rating",
                         height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Premium vs Economy analysis
    st.subheader("💎 Premium vs Economy Experience Gap")
    
    premium_classes = ['Business Class', 'First Class']
    economy_classes = ['Economy Class', 'Premium Economy']
    
    premium_data = df[df['Seat Type'].isin(premium_classes)]
    economy_data = df[df['Seat Type'].isin(economy_classes)]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        premium_satisfaction = premium_data['Overall_Rating'].mean()
        economy_satisfaction = economy_data['Overall_Rating'].mean()
        gap = premium_satisfaction - economy_satisfaction
        st.metric("Premium vs Economy Gap", f"{gap:.2f} points", 
                 delta=f"{gap/economy_satisfaction*100:.1f}% improvement")
        
    with col2:
        premium_rec = (premium_data['Recommended'] == 'yes').mean() * 100
        economy_rec = (economy_data['Recommended'] == 'yes').mean() * 100
        rec_gap = premium_rec - economy_rec
        st.metric("Recommendation Gap", f"{rec_gap:.1f}%")
        
    with col3:
        premium_happy = (premium_data['Overall_Rating'] >= 8).mean() * 100
        economy_happy = (economy_data['Overall_Rating'] >= 8).mean() * 100
        happy_gap = premium_happy - economy_happy
        st.metric("Happiness Gap", f"{happy_gap:.1f}%")

def create_interactive_filters(df):
    """Create interactive filters for the dashboard"""
    st.sidebar.header("🔧 Dashboard Filters")
    
    # Airline filter
    airlines = ['All'] + sorted(df['Airline Name'].dropna().unique().tolist())
    selected_airline = st.sidebar.selectbox("Select Airline", airlines)
    
    # Seat class filter
    seat_classes = ['All'] + sorted(df['Seat Type'].dropna().unique().tolist())
    selected_seat_class = st.sidebar.selectbox("Select Seat Class", seat_classes)
    
    # Traveler type filter
    traveler_types = ['All'] + sorted(df['Type Of Traveller'].dropna().unique().tolist())
    selected_traveler_type = st.sidebar.selectbox("Select Traveler Type", traveler_types)
    
    # Rating range filter
    rating_range = st.sidebar.slider("Rating Range", 1.0, 10.0, (1.0, 10.0), 0.5)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_airline != 'All':
        filtered_df = filtered_df[filtered_df['Airline Name'] == selected_airline]
    
    if selected_seat_class != 'All':
        filtered_df = filtered_df[filtered_df['Seat Type'] == selected_seat_class]
        
    if selected_traveler_type != 'All':
        filtered_df = filtered_df[filtered_df['Type Of Traveller'] == selected_traveler_type]
    
    filtered_df = filtered_df[
        (filtered_df['Overall_Rating'] >= rating_range[0]) & 
        (filtered_df['Overall_Rating'] <= rating_range[1])
    ]
    
    # Show filter summary
    st.sidebar.markdown("---")
    st.sidebar.write(f"**Filtered Dataset:**")
    st.sidebar.write(f"Reviews: {len(filtered_df):,} / {len(df):,}")
    st.sidebar.write(f"Avg Rating: {filtered_df['Overall_Rating'].mean():.2f}")
    st.sidebar.write(f"Happy Rate: {(filtered_df['Overall_Rating'] >= 8).mean()*100:.1f}%")
    
    return filtered_df

def main():
    """Main dashboard function"""
    st.markdown('<div class="main-header">✈️ Airline Experience Analytics Dashboard</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem; color: #666;">
        <h3>Understanding What Makes Passengers Happy vs Frustrated</h3>
        <p>Comprehensive analysis of airline reviews, satisfaction drivers, competitive landscape, and hidden pain points</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df, service_cols = load_and_process_data()
    
    if df is None:
        st.error("Could not load data. Please ensure 'Airline Review.csv' is in the same directory.")
        st.info("💡 Make sure to place the 'Airline Review.csv' file in the same folder as this dashboard.")
        return
    
    # Apply filters
    filtered_df = create_interactive_filters(df)
    
    # Main dashboard sections
    create_satisfaction_overview(filtered_df, service_cols)
    
    st.markdown("---")
    analyze_happiness_drivers(filtered_df, service_cols)
    
    st.markdown("---")
    analyze_review_themes_advanced(filtered_df)
    
    st.markdown("---")
    analyze_competitive_landscape(filtered_df)
    
    st.markdown("---")
    analyze_geographic_performance(filtered_df)
    
    st.markdown("---")
    analyze_class_and_traveler_segments(filtered_df)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p><em>🚀 Dashboard built with Streamlit • Data insights from comprehensive airline review analysis</em></p>
        <p><strong>Key Focus Areas:</strong> Happiness Drivers • Pain Point Detection • Competitive Analysis • Geographic Performance</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()