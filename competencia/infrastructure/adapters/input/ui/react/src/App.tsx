import { RouterProvider } from 'react-router';
import { router } from './routes';
import { AuthProvider } from './context/AuthContext';
import { Toaster } from 'sonner';

function App() {
  return (
    <AuthProvider>
      <Toaster 
        position="top-right" 
        richColors 
        expand={true} 
        closeButton
        theme="light"
      />
      <RouterProvider router={router} />
    </AuthProvider>
  );
}

export default App;
