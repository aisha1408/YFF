import React from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { App } from './modules/App'
import { DiseaseDetailsPage } from './modules/DiseaseDetailsPage'
import { DiseaseListPage } from './modules/DiseaseListPage'
import './styles.css'

const router = createBrowserRouter([
	{
		path: '/',
		element: <App />,
		children: [
			{ index: true, element: <DiseaseListPage /> },
			{ path: 'disease/:id', element: <DiseaseDetailsPage /> },
		],
	},
])

const container = document.getElementById('root')!
createRoot(container).render(<RouterProvider router={router} />)

