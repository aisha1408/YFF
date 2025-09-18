import React from 'react'
import { Outlet, Link } from 'react-router-dom'

export function App(){
	return (
		<div className="container">
			<div className="header">
				<Link to="/" className="title">Crop Disease KB</Link>
			</div>
			<Outlet />
		</div>
	)
}



