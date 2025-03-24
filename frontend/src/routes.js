import { createBrowserRouter } from 'react-router-dom';
import HomePage from './pages/HomePage';
import UploadPage from './pages/UploadPage';
import AnalysisPage from './pages/AnalysisPage';

const router = createBrowserRouter([
  {
    path: '/',
    element: <HomePage />
  },
  {
    path: '/upload',
    element: <UploadPage />
  },
  {
    path: '/analysis/:id',
    element: <AnalysisPage />
  }
]);

export default router;