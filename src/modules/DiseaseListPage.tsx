import React from 'react'
import { Link } from 'react-router-dom'
import { getDiseases } from './data'
import type { Disease } from './types'

export type { Disease }

export function DiseaseListPage(){
	const [q, setQ] = React.useState('')
	const [crop, setCrop] = React.useState<'all' | string>('all')

const all = getDiseases()
	const crops = Array.from(new Set(all.map(d => d.cropName))).sort()

	const list = all.filter(d => {
		const hay = `${d.diseaseName} ${d.cropName}`.toLowerCase()
		const matchesText = hay.includes(q.trim().toLowerCase())
		const matchesCrop = crop === 'all' ? true : d.cropName === crop
		return matchesText && matchesCrop
	})

	return (
		<div>
			<div className="toolbar">
				<div className="search">
					<input
						placeholder="Search by disease or crop"
						value={q}
						onChange={e => setQ(e.target.value)}
					/>
				</div>
				<select className="select" value={crop} onChange={e=>setCrop(e.target.value)}>
					<option value="all">All crops</option>
					{crops.map(c => (<option key={c} value={c}>{c}</option>))}
				</select>
				<div className="count">{list.length} results</div>
			</div>
			<div className="grid">
				{list.map(item => (
					<Link key={item.id} to={`/disease/${item.id}`} className="card">
						<img className="thumb" src={item.imageURL} alt="" onError={(e)=>{(e.currentTarget as HTMLImageElement).src='/assets/placeholder.jpg'}} />
						<div className="card-body">
							<p className="name">{item.diseaseName}</p>
							<p className="meta">{item.cropName}</p>
							<p className="meta truncate-2">{(item.symptoms && item.symptoms.length>0) ? item.symptoms.slice(0,2).join(' • ') : ''}</p>
							<div className="badges">
								{item.severity && (
									<span className={`badge ${item.severity==='high'?'red':item.severity==='medium'?'orange':'green'}`}>{item.severity}</span>
								)}
								{item.season && (<span className="badge">{item.season}</span>)}
								{item.region && (<span className="badge">{item.region}</span>)}
							</div>
						</div>
					</Link>
				))}
			</div>
		</div>
	)
}


