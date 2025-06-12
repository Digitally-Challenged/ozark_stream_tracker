# 🌊 Ozark Stream Tracker

Real-time water level monitoring for Arkansas and Oklahoma whitewater streams. Track paddling conditions with live USGS gauge data.

![Ozark Stream Tracker](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🚀 Features

- **Real-time Gauge Data**: Live water levels from 150+ USGS monitoring stations
- **Stream Conditions**: Visual indicators for optimal paddling conditions
- **Dark Mode**: Eye-friendly dark theme for low-light viewing
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Advanced Filtering**: Filter by difficulty rating and stream size
- **Turner Bend Integration**: Custom gauge reading for Mulberry River at Turner Bend

## 🛠️ Tech Stack

- **Frontend**: React 18, TypeScript, Material-UI 5
- **Build Tool**: Vite
- **Data Source**: USGS Water Services API
- **Deployment**: Netlify

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ozark_stream_tracker.git
cd ozark_stream_tracker
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file (optional):
```bash
cp .env.example .env
```

4. Start the development server:
```bash
npm run dev
```

## 🏗️ Building for Production

```bash
npm run build
```

The build output will be in the `dist` directory.

## 🚀 Deployment

### Deploy to Netlify

1. **Via Netlify CLI**:
```bash
npm install -g netlify-cli
netlify deploy --prod
```

2. **Via GitHub Integration**:
   - Connect your GitHub repository to Netlify
   - Netlify will automatically deploy on push to main branch

3. **Manual Deploy**:
   - Build the project: `npm run build`
   - Drag and drop the `dist` folder to Netlify

### Environment Variables

For production, set these in Netlify's environment variables:

- `VITE_API_URL` - (Optional) Backend API URL for Turner Bend gauge

## 📊 Data Sources

- **USGS Gauges**: Real-time data from United States Geological Survey
- **Turner Bend**: Custom web scraping solution (requires backend service)

## 🎨 Features Overview

### Stream Table
- Sortable columns
- Real-time search
- Color-coded water levels
- Trend indicators (rising/falling/stable)

### Filtering System
- Rating filters (Class I-V, Play spots)
- Size categories (XS to DC/A)
- Persistent filter preferences

### Visual Indicators
- **Green**: Optimal paddling conditions
- **Yellow**: Low but runnable
- **Blue**: High water
- **Red**: Too low to paddle

## 🔧 Development

### Project Structure
```
src/
├── components/       # React components
├── context/         # Theme context
├── data/           # Stream data
├── hooks/          # Custom hooks
├── services/       # API services
├── theme/          # Theme configuration
├── types/          # TypeScript types
└── utils/          # Utility functions
```

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

## 🐛 Known Issues

- Turner Bend gauge requires backend service for CORS
- Some gauges may have delayed readings
- Mobile keyboard may cover input on some devices

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- USGS Water Services for providing gauge data
- Arkansas Canoe Club for stream information
- All the paddlers who contributed stream knowledge

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

Made with ❤️ for the paddling community

[Edit in StackBlitz next generation editor ⚡️](https://stackblitz.com/~/github.com/Digitally-Challenged/ozark_stream_tracker)
