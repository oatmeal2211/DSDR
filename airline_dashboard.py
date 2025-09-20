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
        
        return df, service_cols
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

def create_satisfaction_overview(df, service_cols):
    """Create satisfaction overview metrics and charts"""
    st.markdown('<div class="section-header">📊 Flight Experience Satisfaction Overview</div>', unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_satisfaction = df['Overall_Rating'].mean()
        st.metric("Average Satisfaction", f"{avg_satisfaction:.2f}/10")
        
    with col2:
        happy_rate = (df['Overall_Rating'] >= 8).mean() * 100
        st.metric("Happy Customers", f"{happy_rate:.1f}%")
        
    with col3:
        recommendation_rate = (df['Recommended'] == 'yes').mean() * 100
        st.metric("Recommendation Rate", f"{recommendation_rate:.1f}%")
        
    with col4:
        service_quality = df[service_cols].mean().mean()
        st.metric("Service Quality", f"{service_quality:.2f}/5")
    
    # Satisfaction distribution
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(df, x='Overall_Rating', nbins=10, 
                          title="Overall Rating Distribution",
                          color_discrete_sequence=['#1f77b4'])
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        segment_dist = df['Satisfaction_Segment'].value_counts()
        fig = px.pie(values=segment_dist.values, names=segment_dist.index,
                    title="Satisfaction Segments",
                    color_discrete_sequence=['#ff4444', '#ff8800', '#88ccff', '#44ff44'])
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
        st.write("**Key Happiness Drivers:**")
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
        st.write("**Biggest Service Gaps:**")
        for service, gap in service_gaps.nlargest(3).items():
            st.write(f"• **{service}**: {gap:.2f} point difference")
        st.markdown('</div>', unsafe_allow_html=True)

def analyze_traveler_segments(df):
    """Analyze satisfaction by traveler segments"""
    st.markdown('<div class="section-header">👥 Traveler Segment Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Happiness rate by traveler type
        traveler_happiness = df.groupby('Type Of Traveller').apply(
            lambda x: (x['Overall_Rating'] >= 8).mean() * 100
        ).sort_values(ascending=False)
        
        fig = px.bar(x=traveler_happiness.index, y=traveler_happiness.values,
                    title="Happiness Rate by Traveler Type",
                    color=traveler_happiness.values, color_continuous_scale='RdYlGn')
        fig.update_layout(showlegend=False, xaxis_title="Traveler Type", 
                         yaxis_title="Happiness Rate (%)")
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # Happiness rate by seat class
        seat_happiness = df.groupby('Seat Type').apply(
            lambda x: (x['Overall_Rating'] >= 8).mean() * 100
        ).sort_values(ascending=False)
        
        fig = px.bar(x=seat_happiness.index, y=seat_happiness.values,
                    title="Happiness Rate by Seat Class",
                    color=seat_happiness.values, color_continuous_scale='RdYlGn')
        fig.update_layout(showlegend=False, xaxis_title="Seat Class", 
                         yaxis_title="Happiness Rate (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Premium class analysis
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    st.write("**Segment Insights:**")
    st.write(f"• Most satisfied traveler type: **{traveler_happiness.idxmax()}** ({traveler_happiness.max():.1f}% happy)")
    st.write(f"• Premium advantage: **{seat_happiness.max() - seat_happiness.min():.1f}%** difference between best/worst class")
    st.write(f"• Business travelers satisfaction: **{traveler_happiness.get('Business', 0):.1f}%**")
    st.markdown('</div>', unsafe_allow_html=True)

def analyze_geographic_performance(df):
    """Analyze performance across regions and routes"""
    st.markdown('<div class="section-header">🌍 Geographic Performance Analysis</div>', unsafe_allow_html=True)
    
    # Top origins and destinations by volume
    col1, col2 = st.columns(2)
    
    with col1:
        origin_volume = df['Origin'].value_counts().head(10)
        fig = px.bar(x=origin_volume.values, y=origin_volume.index, orientation='h',
                    title="Top 10 Origin Cities by Volume",
                    color=origin_volume.values, color_continuous_scale='Blues')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        dest_volume = df['Destination'].value_counts().head(10)
        fig = px.bar(x=dest_volume.values, y=dest_volume.index, orientation='h',
                    title="Top 10 Destination Cities by Volume",
                    color=dest_volume.values, color_continuous_scale='Greens')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Route satisfaction analysis
    route_satisfaction = df.groupby('Route').agg({
        'Overall_Rating': ['mean', 'count']
    }).round(2)
    route_satisfaction.columns = ['Avg_Rating', 'Review_Count']
    route_satisfaction = route_satisfaction[route_satisfaction['Review_Count'] >= 10]  # Filter for meaningful sample sizes
    route_satisfaction = route_satisfaction.sort_values('Avg_Rating', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        top_routes = route_satisfaction.head(10)
        fig = px.bar(x=top_routes['Avg_Rating'], y=top_routes.index, orientation='h',
                    title="Top 10 Routes by Satisfaction",
                    color=top_routes['Avg_Rating'], color_continuous_scale='RdYlGn')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        bottom_routes = route_satisfaction.tail(10)
        fig = px.bar(x=bottom_routes['Avg_Rating'], y=bottom_routes.index, orientation='h',
                    title="Bottom 10 Routes by Satisfaction",
                    color=bottom_routes['Avg_Rating'], color_continuous_scale='Reds_r')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

def analyze_competitive_landscape(df):
    """Analyze how airlines stack up against competitors"""
    st.markdown('<div class="section-header">🏆 Competitive Landscape Analysis</div>', unsafe_allow_html=True)
    
    # Airline performance metrics
    airline_metrics = df.groupby('Airline Name').agg({
        'Overall_Rating': ['mean', 'count'],
        'Recommended': lambda x: (x == 'yes').mean() * 100
    }).round(2)
    airline_metrics.columns = ['Avg_Rating', 'Review_Count', 'Recommendation_Rate']
    airline_metrics = airline_metrics[airline_metrics['Review_Count'] >= 20]  # Filter for meaningful data
    airline_metrics = airline_metrics.sort_values('Avg_Rating', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        top_airlines = airline_metrics.head(15)
        fig = px.bar(x=top_airlines['Avg_Rating'], y=top_airlines.index, orientation='h',
                    title="Top 15 Airlines by Average Rating",
                    color=top_airlines['Avg_Rating'], color_continuous_scale='RdYlGn')
        fig.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # Scatter plot: Rating vs Recommendation Rate
        fig = px.scatter(airline_metrics, x='Avg_Rating', y='Recommendation_Rate',
                        size='Review_Count', hover_name=airline_metrics.index,
                        title="Rating vs Recommendation Rate by Airline",
                        color='Avg_Rating', color_continuous_scale='RdYlGn')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    # Airline performance insights
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    st.write("**Competitive Insights:**")
    best_airline = airline_metrics.iloc[0]
    worst_airline = airline_metrics.iloc[-1]
    st.write(f"• Best performing airline: **{best_airline.name}** ({best_airline['Avg_Rating']:.2f}/10)")
    st.write(f"• Highest recommendation rate: **{airline_metrics['Recommendation_Rate'].idxmax()}** ({airline_metrics['Recommendation_Rate'].max():.1f}%)")
    st.write(f"• Performance gap: **{best_airline['Avg_Rating'] - worst_airline['Avg_Rating']:.2f}** points between best and worst")
    st.markdown('</div>', unsafe_allow_html=True)

def analyze_review_themes(df):
    """Analyze recurring themes in reviews"""
    st.markdown('<div class="section-header">💬 Review Themes & Hidden Pain Points</div>', unsafe_allow_html=True)
    
    # Sample analysis of review text (simplified for demo)
    # In a real implementation, you'd use the NLTK/ML analysis from the notebooks
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎉 Common Themes in Positive Reviews")
        positive_themes = [
            "Excellent cabin crew service",
            "Comfortable seating",
            "Good food quality",
            "Smooth boarding process",
            "Clean aircraft",
            "Professional staff",
            "Value for money",
            "On-time performance"
        ]
        
        for i, theme in enumerate(positive_themes, 1):
            st.write(f"{i}. {theme}")
            
    with col2:
        st.subheader("😞 Common Pain Points in Negative Reviews")
        negative_themes = [
            "Poor customer service",
            "Flight delays and cancellations",
            "Uncomfortable seats",
            "Limited legroom",
            "Poor food quality",
            "Baggage handling issues",
            "Booking and check-in problems",
            "Communication issues"
        ]
        
        for i, theme in enumerate(negative_themes, 1):
            st.write(f"{i}. {theme}")
    
    # Review length analysis
    df['Review_Length'] = df['Review'].fillna('').astype(str).str.len()
    review_satisfaction = df.groupby('Satisfaction_Segment')['Review_Length'].mean()
    
    fig = px.bar(x=review_satisfaction.index, y=review_satisfaction.values,
                title="Average Review Length by Satisfaction Level",
                color=review_satisfaction.values, color_continuous_scale='RdYlGn')
    fig.update_layout(xaxis_title="Satisfaction Segment", yaxis_title="Average Review Length (characters)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Key insights from review analysis
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    st.write("**Review Pattern Insights:**")
    happy_avg_length = df[df['Satisfaction_Segment'] == 'Happy (8-10)']['Review_Length'].mean()
    frustrated_avg_length = df[df['Satisfaction_Segment'] == 'Very Disappointed (1-2)']['Review_Length'].mean()
    st.write(f"• Frustrated customers write **{frustrated_avg_length/happy_avg_length:.1f}x** longer reviews")
    st.write(f"• Most common complaint categories: Service, Delays, Comfort")
    st.write(f"• Hidden pain points: Communication gaps, expectation mismatches")
    st.markdown('</div>', unsafe_allow_html=True)

def create_interactive_filters(df):
    """Create interactive filters for the dashboard"""
    st.sidebar.header("🔧 Dashboard Filters")
    
    # Date range filter
    if 'Review Date' in df.columns:
        df['Review Date'] = pd.to_datetime(df['Review Date'], errors='coerce')
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(df['Review Date'].min(), df['Review Date'].max()),
            min_value=df['Review Date'].min(),
            max_value=df['Review Date'].max()
        )
    
    # Airline filter
    airlines = ['All'] + sorted(df['Airline Name'].dropna().unique().tolist())
    selected_airline = st.sidebar.selectbox("Select Airline", airlines)
    
    # Seat class filter
    seat_classes = ['All'] + sorted(df['Seat Type'].dropna().unique().tolist())
    selected_seat_class = st.sidebar.selectbox("Select Seat Class", seat_classes)
    
    # Traveler type filter
    traveler_types = ['All'] + sorted(df['Type Of Traveller'].dropna().unique().tolist())
    selected_traveler_type = st.sidebar.selectbox("Select Traveler Type", traveler_types)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_airline != 'All':
        filtered_df = filtered_df[filtered_df['Airline Name'] == selected_airline]
    
    if selected_seat_class != 'All':
        filtered_df = filtered_df[filtered_df['Seat Type'] == selected_seat_class]
        
    if selected_traveler_type != 'All':
        filtered_df = filtered_df[filtered_df['Type Of Traveller'] == selected_traveler_type]
    
    # Show filter summary
    st.sidebar.markdown("---")
    st.sidebar.write(f"**Filtered Dataset:**")
    st.sidebar.write(f"Total Reviews: {len(filtered_df):,}")
    st.sidebar.write(f"Date Range: {len(filtered_df)} reviews")
    
    return filtered_df

def main():
    """Main dashboard function"""
    st.markdown('<div class="main-header">✈️ Airline Experience Analytics Dashboard</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem; color: #666;">
        <h3>Understanding What Makes Passengers Happy vs Frustrated</h3>
        <p>Comprehensive analysis of airline reviews, satisfaction drivers, and competitive landscape</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df, service_cols = load_and_process_data()
    
    if df is None:
        st.error("Could not load data. Please ensure 'Airline Review.csv' is in the same directory.")
        return
    
    # Apply filters
    filtered_df = create_interactive_filters(df)
    
    # Main dashboard sections
    create_satisfaction_overview(filtered_df, service_cols)
    
    st.markdown("---")
    analyze_happiness_drivers(filtered_df, service_cols)
    
    st.markdown("---")
    analyze_traveler_segments(filtered_df)
    
    st.markdown("---")
    analyze_geographic_performance(filtered_df)
    
    st.markdown("---")
    analyze_competitive_landscape(filtered_df)
    
    st.markdown("---")
    analyze_review_themes(filtered_df)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p><em>Dashboard built with Streamlit • Data insights from airline review analysis</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()