# Solar Site Analyzer - Frontend

A modern, production-ready Vue3 web application for identifying and analyzing potential sites for solar panel installations using spatial data analysis.

## 🌟 Features

- **Interactive Map Visualization**: Powered by Mapbox GL JS with custom markers and popups
- **Dynamic Weight Adjustment**: Real-time suitability score recalculation with custom factor weights
- **Advanced Filtering**: Filter sites by score range with instant map updates
- **Site Cards**: Horizontally scrollable bottom bar with ranked site cards
- **Responsive Design**: Modern, dark-themed UI built with Tailwind CSS
- **Type-Safe**: Full TypeScript support for enhanced developer experience
- **State Management**: Centralized state management with Pinia
- **Production-Ready**: Optimized build configuration with Vite

## 🏗️ Architecture

```
frontend/
├── src/
│   ├── components/          # Vue components
│   │   ├── Header.vue       # Top header with statistics
│   │   ├── Sidebar.vue      # Left sidebar with controls
│   │   ├── MapView.vue      # Mapbox GL JS map component
│   │   ├── BottomSiteBar.vue # Scrollable site cards
│   │   ├── SiteCard.vue     # Individual site card
│   │   ├── SitePopup.vue    # Site details popup
│   │   └── ...              # Utility components
│   ├── stores/              # Pinia stores
│   │   └── siteStore.ts     # Main application state
│   ├── services/            # API services
│   │   └── api.ts           # API client
│   ├── types/               # TypeScript types
│   │   └── index.ts         # Type definitions
│   ├── config/              # Configuration
│   │   └── index.ts         # App configuration
│   ├── App.vue              # Root component
│   ├── main.ts              # Application entry point
│   └── style.css            # Global styles
├── public/                  # Static assets
├── index.html              # HTML template
├── package.json            # Dependencies
├── vite.config.ts          # Vite configuration
├── tsconfig.json           # TypeScript configuration
└── tailwind.config.js      # Tailwind CSS configuration
```

## 📋 Prerequisites

- Node.js (v18 or higher)
- npm or yarn
- Mapbox Access Token (get one from [Mapbox](https://account.mapbox.com/))
- Backend API running on `http://localhost:8000`

## 🚀 Getting Started

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create a `.env` file in the frontend directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Mapbox token:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_MAPBOX_TOKEN=your_mapbox_access_token_here
```

### 3. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### 4. Build for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

### 5. Preview Production Build

```bash
npm run preview
```

## 🎯 Key Features Explained

### Weight Adjustment System

The application allows you to adjust five factors that contribute to the suitability score:

1. **Solar Irradiance** (default: 35%) - Amount of solar energy available
2. **Available Area** (default: 25%) - Size of the potential installation site
3. **Grid Distance** (default: 20%) - Proximity to electrical grid
4. **Terrain Slope** (default: 15%) - Ground inclination
5. **Infrastructure** (default: 5%) - Proximity to roads and facilities

All weights must sum to 1.00 (100%) before recalculation.

### Score Filtering

Filter sites displayed on the map by setting minimum and maximum suitability scores (0-100).

### Site Selection

- Click on any marker on the map to select a site
- Click on a site card in the bottom bar to center and highlight it on the map
- Selected sites show detailed information in a popup

### Score Color Coding

Sites are color-coded based on their suitability scores:
- 🟢 **Excellent** (80-100): Best sites for installation
- 🟡 **Good** (60-79): High potential sites
- 🟠 **Moderate** (40-59): Acceptable sites with considerations
- 🟠 **Poor** (20-39): Limited suitability
- 🔴 **Very Poor** (0-19): Not recommended

## 🔌 API Integration

The frontend communicates with the backend API at the following endpoints:

- `GET /api/v1/sites` - Fetch sites with optional filters
- `GET /api/v1/sites/{id}` - Get detailed site information
- `POST /api/v1/analyze` - Recalculate scores with custom weights
- `GET /api/v1/statistics` - Get summary statistics

## 🎨 Technology Stack

- **Framework**: Vue 3 (Composition API)
- **Build Tool**: Vite
- **Language**: TypeScript
- **State Management**: Pinia
- **Styling**: Tailwind CSS
- **Maps**: Mapbox GL JS
- **Icons**: Lucide Vue Next
- **HTTP Client**: Axios
- **Date Formatting**: date-fns

## 📱 Responsive Design

The application is fully responsive and works seamlessly on:
- Desktop (1920px and above)
- Laptop (1024px - 1919px)
- Tablet (768px - 1023px)
- Mobile (320px - 767px)

## 🐛 Troubleshooting

### Map Not Loading

- Ensure your Mapbox token is correctly set in `.env`
- Check browser console for errors
- Verify the token is valid and has the required scopes

### API Connection Issues

- Ensure the backend is running on `http://localhost:8000`
- Check CORS configuration in the backend
- Verify proxy configuration in `vite.config.ts`

### Build Errors

- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Clear Vite cache: `rm -rf node_modules/.vite`
- Check TypeScript errors: `npm run type-check`

## 🔒 Security Considerations

- Never commit `.env` file with real tokens
- Use environment variables for sensitive data
- Implement proper authentication for production
- Enable HTTPS in production

## 🚀 Deployment

### Using Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Using Docker

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 📄 License

This project is part of the Solar Site Analyzer system.

## 👨‍💻 Development

### Code Style

- Use Composition API for Vue components
- Follow TypeScript strict mode
- Use meaningful component and variable names
- Keep components small and focused
- Write self-documenting code

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add your feature description"

# Push and create PR
git push origin feature/your-feature-name
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📞 Support

For issues, questions, or contributions, please open an issue in the repository.
