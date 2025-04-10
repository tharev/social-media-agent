# social-media-agent
Social media team of agents
# Social Media Agent System

An open-source social media management system with AI-powered content generation and automated posting for multiple platforms.

## Overview

This system provides a comprehensive solution for managing social media presence across Facebook, X (Twitter), Instagram, and TikTok. It features a team leader agent that coordinates with platform-specific agents to generate and post content, collect metrics, and provide regular performance reports.

## Features

- **Team Structure**: 1 team leader agent and 4 platform-specific agents
- **Platforms Supported**: Facebook, X (Twitter), Instagram, TikTok
- **AI-Powered Content**: Text and image generation using LLMs
- **Content Optimization**: Platform-specific content adaptation
- **Scheduling**: Automated content posting at optimal times
- **Analytics**: Comprehensive metrics collection and analysis
- **Reporting**: Weekly progress reports with performance insights
- **Customizable**: Extensive configuration options for your brand

## Architecture

The system is organized into several key components:

- **Team Leader**: Coordinates activities, schedules content, and generates reports
- **Platform Agents**: Handle platform-specific posting and metrics collection
- **LLM Integration**: Connects to text and image generation models
- **Content Generation**: Creates optimized content for each platform
- **Reporting System**: Collects metrics and generates performance reports

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/social-media-agent.git
cd social-media-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your API keys:
   - Copy `config/config.py` to `config/config_local.py`
   - Add your API keys and customize settings in `config_local.py`

## Usage

### Basic Usage

```python
from src.team_leader.team_leader import TeamLeader
from config.config import get_config

# Load configuration
config = get_config()

# Initialize the team leader
team_leader = TeamLeader(config=config)

# Generate and post content
team_leader.generate_and_post_content(
    platform="twitter",
    topic="industry news",
    content_type="text"
)

# Generate a weekly report
report = team_leader.generate_weekly_report()
```

### Scheduling Content

```python
# Schedule content for later posting
team_leader.schedule_content(
    platform="instagram",
    topic="product showcase",
    content_type="image",
    schedule_time="2025-03-22 15:00:00"
)

# Run the scheduler to process pending tasks
team_leader.run_scheduler()
```

### Generating Reports

```python
# Generate a platform-specific report
report = team_leader.generate_platform_report(
    platform="facebook",
    start_date="2025-03-01",
    end_date="2025-03-21"
)

# Generate a performance dashboard
dashboard = team_leader.generate_performance_dashboard(days=30)
```

## Configuration

The system is highly configurable through the `config/config.py` file:

- **API Keys**: Set your LLM and social media platform API credentials
- **Platform Settings**: Configure posting frequency, best times, and content types
- **Content Settings**: Define your brand voice, themes, and target audience
- **LLM Settings**: Choose providers and models for text and image generation
- **Reporting Settings**: Set report schedule and recipients
- **System Settings**: Configure logging, directories, and other system parameters

## Testing

Run the test suite to ensure everything is working correctly:

```bash
pytest tests/
```

For coverage information:

```bash
pytest tests/ --cov=src/ --cov-report=term
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
