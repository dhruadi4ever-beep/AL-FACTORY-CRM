# ARYAN LACE Manager

This workspace contains the initial backend and Android app foundation for ARYAN LACE Manager based on Chapter 1 of the business logic.

## Backend
- FastAPI service with dynamic master-data and event endpoints
- PostgreSQL-ready SQLAlchemy models
- Dashboard and assistant alert endpoints

## Android
- Kotlin + Jetpack Compose app shell
- Dashboard view for factory operations

## Web
- Vite + React web frontend in `web/`
- Firebase Hosting setup ready for project `al-factory-crm`

## Hosting setup
### Web hosting
1. Install Firebase CLI
   ```bash
   npm install -g firebase-tools
   ```
2. Build the web app
   ```bash
   cd web
   npm install
   npm run build
   ```
3. Deploy to Firebase
   ```bash
   cd ..
   firebase deploy --only hosting
   ```

### Android Firebase setup
1. In Firebase Console, add Android app to project `al-factory-crm`
2. Download `google-services.json`
3. Place it at `android/app/google-services.json`
4. Update Gradle with Firebase SDK and initialize Firebase in `MainActivity.kt`

### Backend deployment
- Deploy the backend separately to Render, then use the public Render URL from the web and Android apps.

## Next steps
- Provide the next chapter for deeper business rules.
- Clarify any workflow decisions before expanding the implementation.
