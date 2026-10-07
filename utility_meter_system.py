"""
Smart Utility Meter Reading System
Using IoT for Automated Water, Gas, and Electricity Consumption Monitoring
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.size'] = 10

class SmartMeter:
    """Represents a smart utility meter (water, gas, or electricity)"""
    
    def __init__(self, meter_id, meter_type, location, consumer_id, consumer_name):
        self.meter_id = meter_id
        self.meter_type = meter_type  # 'electricity', 'water', 'gas'
        self.location = location
        self.consumer_id = consumer_id
        self.consumer_name = consumer_name
        self.current_reading = 0.0
        self.previous_reading = 0.0
        self.reading_history = []
        self.last_reading_time = None
        self.meter_status = 'operational'
        self.battery_level = 100  # For wireless meters
        self.signal_strength = -60  # dBm
        self.anomalies_detected = 0
        
        # Unit-specific parameters
        if meter_type == 'electricity':
            self.unit = 'kWh'
            self.daily_consumption_baseline = 15.0  # kWh
            self.daily_variance = 3.0
        elif meter_type == 'water':
            self.unit = 'liters'
            self.daily_consumption_baseline = 200.0  # liters
            self.daily_variance = 50.0
        else:  # gas
            self.unit = 'cubic meters'
            self.daily_consumption_baseline = 0.5
            self.daily_variance = 0.1
    
    def record_reading(self, timestamp, consumption_delta):
        """Record a meter reading with realistic consumption patterns"""
        # Add realistic noise to consumption
        noise = np.random.normal(0, 0.05 * consumption_delta)
        actual_consumption = max(0, consumption_delta + noise)
        
        self.previous_reading = self.current_reading
        self.current_reading += actual_consumption
        
        # Simulate battery drain for wireless meters
        if self.battery_level > 5:
            self.battery_level -= np.random.uniform(0.1, 0.3)
        
        # Simulate signal variation
        self.signal_strength = -60 + np.random.normal(0, 5)
        
        reading_record = {
            'meter_id': self.meter_id,
            'meter_type': self.meter_type,
            'timestamp': timestamp,
            'reading': self.current_reading,
            'consumption_delta': actual_consumption,
            'unit': self.unit,
            'battery_level': self.battery_level,
            'signal_strength': self.signal_strength,
            'status': self.meter_status
        }
        
        self.reading_history.append(reading_record)
        self.last_reading_time = timestamp
        
        return reading_record
    
    def detect_anomaly(self, expected_consumption, actual_consumption, threshold=0.3):
        """Detect anomalous consumption patterns"""
        if actual_consumption > expected_consumption * (1 + threshold):
            self.anomalies_detected += 1
            return True, 'High consumption detected'
        elif actual_consumption < expected_consumption * (1 - threshold) and actual_consumption > 0:
            return True, 'Low consumption detected'
        return False, 'Normal consumption'
    
    def get_meter_status(self):
        """Get comprehensive meter status"""
        status = {
            'meter_id': self.meter_id,
            'meter_type': self.meter_type,
            'current_reading': self.current_reading,
            'battery_level': self.battery_level,
            'signal_strength': self.signal_strength,
            'status': self.meter_status,
            'anomalies': self.anomalies_detected,
            'last_reading': self.last_reading_time
        }
        return status


class ConsumptionAnalyzer:
    """Analyzes consumption patterns and generates insights"""
    
    def __init__(self):
        self.consumption_records = []
        self.anomaly_logs = []
        self.billing_records = []
    
    def analyze_consumption(self, meter, timestamp, hour_of_day):
        """Analyze consumption based on time patterns"""
        # Realistic consumption patterns based on time of day
        if meter.meter_type == 'electricity':
            # Peak hours: 7-9 AM, 6-11 PM
            if (7 <= hour_of_day <= 9) or (18 <= hour_of_day <= 23):
                base_consumption = meter.daily_consumption_baseline * 1.5
            # Off-peak: 12 AM - 6 AM
            elif 0 <= hour_of_day < 6:
                base_consumption = meter.daily_consumption_baseline * 0.3
            else:
                base_consumption = meter.daily_consumption_baseline * 0.8
        
        elif meter.meter_type == 'water':
            # Peak hours: 7-9 AM, 6-8 PM
            if (7 <= hour_of_day <= 9) or (18 <= hour_of_day <= 20):
                base_consumption = meter.daily_consumption_baseline * 1.3
            # Low usage: 11 PM - 5 AM
            elif 23 <= hour_of_day or hour_of_day < 5:
                base_consumption = meter.daily_consumption_baseline * 0.2
            else:
                base_consumption = meter.daily_consumption_baseline * 0.6
        
        else:  # gas
            # Peak hours: 7-9 AM, 5-10 PM (heating/cooking)
            if (7 <= hour_of_day <= 9) or (17 <= hour_of_day <= 22):
                base_consumption = meter.daily_consumption_baseline * 1.4
            # Low usage: 10 AM - 4 PM
            elif 10 <= hour_of_day <= 16:
                base_consumption = meter.daily_consumption_baseline * 0.4
            else:
                base_consumption = meter.daily_consumption_baseline * 0.7
        
        # Add daily variance
        variance = np.random.normal(0, meter.daily_variance / 100 * base_consumption)
        consumption = max(0, base_consumption + variance)
        
        return consumption
    
    def generate_billing_record(self, meter, period_start, period_end, rate_per_unit):
        """Generate billing information"""
        period_readings = [r for r in meter.reading_history 
                          if period_start <= r['timestamp'] <= period_end]
        
        if not period_readings:
            total_consumption = 0
        else:
            total_consumption = period_readings[-1]['reading'] - period_readings[0]['reading']
        
        billing_amount = total_consumption * rate_per_unit
        
        billing_record = {
            'meter_id': meter.meter_id,
            'consumer_id': meter.consumer_id,
            'consumer_name': meter.consumer_name,
            'meter_type': meter.meter_type,
            'period_start': period_start,
            'period_end': period_end,
            'total_consumption': total_consumption,
            'unit': meter.unit,
            'rate_per_unit': rate_per_unit,
            'billing_amount': billing_amount,
            'anomalies_detected': meter.anomalies_detected
        }
        
        self.billing_records.append(billing_record)
        return billing_record


class SmartUtilityMeterSystem:
    """Main system managing utility meter monitoring"""
    
    def __init__(self, system_name='Smart Utility Meter Reading System'):
        self.system_name = system_name
        self.meters = {}
        self.analyzer = ConsumptionAnalyzer()
        self.daily_reports = []
        self.system_status = 'operational'
        self.total_readings = 0
        self.anomalies_detected = 0
        
        # Billing rates
        self.rates = {
            'electricity': 8.5,  # per kWh
            'water': 0.05,       # per liter
            'gas': 15.0          # per cubic meter
        }
    
    def add_meter(self, meter_id, meter_type, location, consumer_id, consumer_name):
        """Add a meter to the system"""
        meter = SmartMeter(meter_id, meter_type, location, consumer_id, consumer_name)
        self.meters[meter_id] = meter
        return meter
    
    def simulate_meter_readings(self, date=None, num_intervals=96):
        """
        Simulate meter readings for a full day with 15-minute intervals
        """
        if date is None:
            date = datetime.now().date()
        
        daily_data = []
        
        # Simulate readings for each 15-minute interval
        for interval in range(num_intervals):
            quarter_hour = (interval * 15) / 60
            hour = int(quarter_hour)
            minutes = int((quarter_hour % 1) * 60)
            
            current_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=quarter_hour)
            
            for meter_id, meter in self.meters.items():
                # Analyze expected consumption
                expected_consumption = self.analyzer.analyze_consumption(meter, current_time, hour)
                
                # Record reading
                reading = meter.record_reading(current_time, expected_consumption)
                
                # Detect anomalies
                is_anomaly, anomaly_type = meter.detect_anomaly(
                    expected_consumption, 
                    expected_consumption,
                    threshold=0.4
                )
                
                if is_anomaly:
                    self.anomalies_detected += 1
                
                self.total_readings += 1
                
                daily_data.append({
                    'timestamp': current_time,
                    'date': date,
                    'hour': hour,
                    'minute': minutes,
                    'meter_id': meter_id,
                    'meter_type': meter.meter_type,
                    'location': meter.location,
                    'consumer_name': meter.consumer_name,
                    'reading': reading['reading'],
                    'consumption_delta': reading['consumption_delta'],
                    'unit': meter.unit,
                    'battery_level': reading['battery_level'],
                    'signal_strength': reading['signal_strength'],
                    'status': reading['status'],
                    'anomaly': is_anomaly,
                    'anomaly_type': anomaly_type
                })
        
        return pd.DataFrame(daily_data)
    
    def get_system_report(self):
        """Generate comprehensive system report"""
        report = {
            'system_name': self.system_name,
            'total_meters': len(self.meters),
            'total_readings': self.total_readings,
            'anomalies_detected': self.anomalies_detected,
            'system_status': self.system_status,
            'meter_types': {}
        }
        
        # Count meters by type
        for meter_id, meter in self.meters.items():
            meter_type = meter.meter_type
            if meter_type not in report['meter_types']:
                report['meter_types'][meter_type] = 0
            report['meter_types'][meter_type] += 1
        
        return report


def generate_visualizations(system, daily_data):
    """Generate comprehensive visualizations for the report"""
    
    # 1. Consumption Analysis by Meter Type
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Smart Utility Meter Reading System - Consumption Analysis', 
                 fontsize=16, fontweight='bold')
    
    # Consumption by hour for each meter type
    for idx, meter_type in enumerate(['electricity', 'water', 'gas']):
        if idx < 3:
            ax = axes[idx // 2, idx % 2]
            meter_data = daily_data[daily_data['meter_type'] == meter_type]
            
            if not meter_data.empty:
                hourly_consumption = meter_data.groupby('hour')['consumption_delta'].sum()
                ax.bar(hourly_consumption.index, hourly_consumption.values, 
                      color=['#3498DB', '#2ECC71', '#E74C3C'][idx], 
                      edgecolor='black', alpha=0.7)
                ax.set_title(f'{meter_type.capitalize()} Consumption by Hour', fontweight='bold')
                ax.set_ylabel(f'Consumption ({meter_data["unit"].iloc[0]})')
                ax.set_xlabel('Hour of Day')
                ax.grid(True, alpha=0.3, axis='y')
    
    # Total consumption by meter type
    ax = axes[1, 1]
    meter_type_consumption = daily_data.groupby('meter_type')['consumption_delta'].sum()
    colors = ['#3498DB', '#2ECC71', '#E74C3C']
    ax.pie(meter_type_consumption.values, labels=meter_type_consumption.index, 
           autopct='%1.1f%%', colors=colors, startangle=90, textprops={'fontweight': 'bold'})
    ax.set_title('Total Consumption Distribution by Type', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/utility_meter_project/fig_consumption_analysis.png', dpi=300, bbox_inches='tight')
    print("Saved: fig_consumption_analysis.png")
    plt.close()
    
    # 2. Meter Status and Health Analysis
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Meter Status and System Health Metrics', fontsize=16, fontweight='bold')
    
    # Battery levels by meter
    meter_battery = daily_data.groupby('meter_id')['battery_level'].mean()
    axes[0, 0].barh(meter_battery.index, meter_battery.values, 
                    color='#F39C12', edgecolor='black', alpha=0.7)
    axes[0, 0].axvline(x=20, color='red', linestyle='--', linewidth=2, label='Low Battery Threshold')
    axes[0, 0].set_title('Average Battery Level by Meter', fontweight='bold')
    axes[0, 0].set_xlabel('Battery Level (%)')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3, axis='x')
    
    # Signal strength distribution
    signal_data = daily_data['signal_strength'].values
    axes[0, 1].hist(signal_data, bins=20, color='#9B59B6', edgecolor='black', alpha=0.7)
    axes[0, 1].axvline(x=signal_data.mean(), color='red', linestyle='--', linewidth=2, 
                       label=f'Mean: {signal_data.mean():.1f} dBm')
    axes[0, 1].set_title('Signal Strength Distribution', fontweight='bold')
    axes[0, 1].set_xlabel('Signal Strength (dBm)')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3, axis='y')
    
    # Anomalies detected by meter
    anomaly_data = daily_data[daily_data['anomaly'] == True].groupby('meter_id').size()
    if not anomaly_data.empty:
        axes[1, 0].bar(range(len(anomaly_data)), anomaly_data.values, 
                      color='#E74C3C', edgecolor='black', alpha=0.7)
        axes[1, 0].set_title('Anomalies Detected by Meter', fontweight='bold')
        axes[1, 0].set_ylabel('Number of Anomalies')
        axes[1, 0].set_xlabel('Meter ID')
        axes[1, 0].set_xticks(range(len(anomaly_data)))
        axes[1, 0].set_xticklabels(anomaly_data.index, rotation=45, ha='right')
        axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # Meter status distribution
    status_counts = daily_data['status'].value_counts()
    axes[1, 1].pie(status_counts.values, labels=status_counts.index, 
                   autopct='%1.1f%%', colors=['#2ECC71', '#E74C3C'], 
                   startangle=90, textprops={'fontweight': 'bold'})
    axes[1, 1].set_title('Meter Status Distribution', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/utility_meter_project/fig_meter_health.png', dpi=300, bbox_inches='tight')
    print("Saved: fig_meter_health.png")
    plt.close()
    
    # 3. System Architecture Diagram
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    
    ax.text(0.5, 0.95, 'Smart Utility Meter Reading System Architecture', 
            ha='center', fontsize=16, fontweight='bold', transform=ax.transAxes)
    
    components = [
        ('Smart Meters\n(Water, Gas, Electricity)', 0.15, 0.75),
        ('IoT\nGateway', 0.5, 0.75),
        ('Cloud\nServer', 0.85, 0.75),
        ('Meter\nDatabase', 0.15, 0.50),
        ('Consumption\nAnalyzer', 0.5, 0.50),
        ('Alert\nSystem', 0.85, 0.50),
        ('Consumer\nDashboard', 0.5, 0.25),
    ]
    
    for label, x, y in components:
        bbox = dict(boxstyle='round,pad=0.6', facecolor='lightblue', edgecolor='black', linewidth=2)
        ax.text(x, y, label, ha='center', va='center', fontsize=11, fontweight='bold',
                transform=ax.transAxes, bbox=bbox)
    
    connections = [
        ((0.25, 0.75), (0.4, 0.75)),
        ((0.6, 0.75), (0.75, 0.75)),
        ((0.15, 0.65), (0.15, 0.55)),
        ((0.5, 0.65), (0.5, 0.55)),
        ((0.85, 0.65), (0.85, 0.55)),
        ((0.5, 0.40), (0.5, 0.35)),
    ]
    
    for start, end in connections:
        ax.annotate('', xy=end, xytext=start, transform=ax.transAxes,
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    features_text = 'Key Features:\n• Real-time Consumption Monitoring\n• Automated Meter Reading\n• Anomaly Detection\n• Billing Automation\n• Energy Efficiency Insights'
    ax.text(0.5, 0.10, features_text, ha='center', va='top', fontsize=10,
            transform=ax.transAxes, bbox=dict(boxstyle='round', facecolor='lightyellow', 
            edgecolor='black', linewidth=1.5))
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/utility_meter_project/fig_system_architecture.png', dpi=300, bbox_inches='tight')
    print("Saved: fig_system_architecture.png")
    plt.close()
    
    # 4. Hourly Consumption Trends
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Hourly Consumption Trends by Meter Type', fontsize=14, fontweight='bold')
    
    meter_types = ['electricity', 'water', 'gas']
    colors_trend = ['#3498DB', '#2ECC71', '#E74C3C']
    
    for idx, meter_type in enumerate(meter_types):
        meter_data = daily_data[daily_data['meter_type'] == meter_type]
        if not meter_data.empty:
            hourly_avg = meter_data.groupby('hour')['consumption_delta'].mean()
            axes[idx].plot(hourly_avg.index, hourly_avg.values, marker='o', linewidth=2.5,
                          markersize=8, color=colors_trend[idx], label=meter_type.capitalize())
            axes[idx].fill_between(hourly_avg.index, hourly_avg.values, alpha=0.3, color=colors_trend[idx])
            axes[idx].set_title(f'{meter_type.capitalize()} Hourly Trend', fontweight='bold')
            axes[idx].set_ylabel(f'Avg Consumption ({meter_data["unit"].iloc[0]})')
            axes[idx].set_xlabel('Hour of Day')
            axes[idx].grid(True, alpha=0.3)
            axes[idx].legend()
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/utility_meter_project/fig_hourly_trends.png', dpi=300, bbox_inches='tight')
    print("Saved: fig_hourly_trends.png")
    plt.close()
    
    # 5. Billing Summary
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Billing and Cost Analysis', fontsize=16, fontweight='bold')
    
    # Estimated daily costs by meter type
    meter_types_list = daily_data['meter_type'].unique()
    rates = {'electricity': 8.5, 'water': 0.05, 'gas': 15.0}
    
    costs = []
    labels = []
    for meter_type in meter_types_list:
        meter_data = daily_data[daily_data['meter_type'] == meter_type]
        total_consumption = meter_data['consumption_delta'].sum()
        cost = total_consumption * rates[meter_type]
        costs.append(cost)
        labels.append(meter_type.capitalize())
    
    axes[0, 0].bar(labels, costs, color=['#3498DB', '#2ECC71', '#E74C3C'], 
                   edgecolor='black', alpha=0.7)
    axes[0, 0].set_title('Estimated Daily Cost by Utility Type', fontweight='bold')
    axes[0, 0].set_ylabel('Cost (Currency Units)')
    axes[0, 0].grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(costs):
        axes[0, 0].text(i, v + 0.5, f'${v:.2f}', ha='center', fontweight='bold')
    
    # Consumption vs cost correlation
    meter_data_elec = daily_data[daily_data['meter_type'] == 'electricity']
    if not meter_data_elec.empty:
        hourly_consumption = meter_data_elec.groupby('hour')['consumption_delta'].sum()
        hourly_cost = hourly_consumption * rates['electricity']
        axes[0, 1].scatter(hourly_consumption.values, hourly_cost.values, 
                          s=100, alpha=0.6, color='#3498DB', edgecolor='black')
        axes[0, 1].set_title('Electricity: Consumption vs Cost', fontweight='bold')
        axes[0, 1].set_xlabel('Consumption (kWh)')
        axes[0, 1].set_ylabel('Cost (Currency Units)')
        axes[0, 1].grid(True, alpha=0.3)
    
    # Peak vs Off-peak consumption
    peak_hours = [7, 8, 9, 18, 19, 20, 21, 22, 23]
    peak_data = daily_data[daily_data['hour'].isin(peak_hours)]
    offpeak_data = daily_data[~daily_data['hour'].isin(peak_hours)]
    
    peak_consumption = peak_data['consumption_delta'].sum()
    offpeak_consumption = offpeak_data['consumption_delta'].sum()
    
    axes[1, 0].bar(['Peak Hours', 'Off-Peak Hours'], 
                   [peak_consumption, offpeak_consumption],
                   color=['#E74C3C', '#2ECC71'], edgecolor='black', alpha=0.7)
    axes[1, 0].set_title('Peak vs Off-Peak Consumption', fontweight='bold')
    axes[1, 0].set_ylabel('Total Consumption')
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # Monthly projection
    daily_total_cost = sum(costs)
    monthly_projection = daily_total_cost * 30
    
    axes[1, 1].text(0.5, 0.7, 'Monthly Cost Projection', ha='center', fontsize=14, 
                   fontweight='bold', transform=axes[1, 1].transAxes)
    axes[1, 1].text(0.5, 0.4, f'${monthly_projection:.2f}', ha='center', fontsize=32, 
                   fontweight='bold', transform=axes[1, 1].transAxes, color='#E74C3C')
    axes[1, 1].text(0.5, 0.15, f'(Based on daily average: ${daily_total_cost:.2f})', 
                   ha='center', fontsize=10, transform=axes[1, 1].transAxes)
    axes[1, 1].axis('off')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/utility_meter_project/fig_billing_analysis.png', dpi=300, bbox_inches='tight')
    print("Saved: fig_billing_analysis.png")
    plt.close()


def main():
    """Main execution function"""
    print("=" * 70)
    print("SMART UTILITY METER READING SYSTEM SIMULATION")
    print("=" * 70)
    
    # Initialize system
    system = SmartUtilityMeterSystem("Smart Utility Meter Reading System")
    
    # Add meters for different consumers
    consumers = [
        ('CONS-001', 'Residential Building A'),
        ('CONS-002', 'Residential Building B'),
        ('CONS-003', 'Commercial Complex'),
    ]
    
    meter_configs = [
        ('METER-E-001', 'electricity', 'Building A - Main', 'CONS-001', 'Residential Building A'),
        ('METER-W-001', 'water', 'Building A - Main', 'CONS-001', 'Residential Building A'),
        ('METER-G-001', 'gas', 'Building A - Main', 'CONS-001', 'Residential Building A'),
        ('METER-E-002', 'electricity', 'Building B - Main', 'CONS-002', 'Residential Building B'),
        ('METER-W-002', 'water', 'Building B - Main', 'CONS-002', 'Residential Building B'),
        ('METER-G-002', 'gas', 'Building B - Main', 'CONS-002', 'Residential Building B'),
        ('METER-E-003', 'electricity', 'Commercial - Main', 'CONS-003', 'Commercial Complex'),
        ('METER-W-003', 'water', 'Commercial - Main', 'CONS-003', 'Commercial Complex'),
        ('METER-G-003', 'gas', 'Commercial - Main', 'CONS-003', 'Commercial Complex'),
    ]
    
    for meter_id, meter_type, location, consumer_id, consumer_name in meter_configs:
        system.add_meter(meter_id, meter_type, location, consumer_id, consumer_name)
    
    print(f"\nSystem initialized with {len(meter_configs)} meters:")
    for meter_id, meter_type, location, _, _ in meter_configs:
        print(f"  - {meter_id}: {meter_type.capitalize()} at {location}")
    
    # Simulate 7 days
    print("\nSimulating 7 days of meter readings...")
    all_data = []
    
    for day in range(7):
        simulation_date = datetime.now().date() - timedelta(days=6-day)
        daily_data = system.simulate_meter_readings(simulation_date)
        all_data.append(daily_data)
        
        report = system.get_system_report()
        print(f"Day {day+1}: Readings={report['total_readings']}, "
              f"Anomalies={report['anomalies_detected']}")
    
    # Combine all data
    combined_data = pd.concat(all_data, ignore_index=True)
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    generate_visualizations(system, combined_data)
    
    # Generate report data
    report = system.get_system_report()
    
    print("\n" + "=" * 70)
    print("SYSTEM REPORT")
    print("=" * 70)
    print(f"System Name: {report['system_name']}")
    print(f"Total Meters: {report['total_meters']}")
    print(f"Total Readings: {report['total_readings']}")
    print(f"Anomalies Detected: {report['anomalies_detected']}")
    print(f"System Status: {report['system_status']}")
    print(f"Meter Types: {report['meter_types']}")
    print("=" * 70)
    
    # Save data to CSV
    combined_data.to_csv('/home/ubuntu/utility_meter_project/meter_readings.csv', index=False)
    print("\nMeter readings saved to: meter_readings.csv")
    
    # Save report to JSON
    report_json = {
        'system_report': report,
        'meters': [{'id': mid, 'type': m.meter_type, 'location': m.location} 
                  for mid, m in system.meters.items()],
        'simulation_date': datetime.now().isoformat(),
        'total_meters': len(system.meters),
        'simulation_days': 7
    }
    
    with open('/home/ubuntu/utility_meter_project/system_report.json', 'w') as f:
        json.dump(report_json, f, indent=2, default=str)
    
    print("System report saved to: system_report.json")
    
    return system, combined_data


if __name__ == "__main__":
    system, data = main()
