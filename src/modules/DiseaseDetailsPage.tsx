import React from 'react'
import { Link, useParams } from 'react-router-dom'
import { getDiseases } from './data'
import type { Disease } from './types'

export function DiseaseDetailsPage(){
	const { id } = useParams()
const disease = (getDiseases() as Disease[]).find(d => d.id === id)

	if(!disease){
		return (
			<div>
				<Link className="back" to="/">Back</Link>
				<p>Not found</p>
			</div>
		)
	}

	return (
		<div>
			<Link className="back" to="/">Back</Link>
			<div className="details">
				<img src={disease.imageURL} alt="" onError={(e)=>{(e.currentTarget as HTMLImageElement).src='/assets/placeholder.jpg'}} />
				<div>
					<h2 className="name">{disease.diseaseName}</h2>
					<p className="meta">{disease.cropName}</p>
					<div className="badges" style={{marginBottom:8}}>
						{disease.severity && (
							<span className={`badge ${disease.severity==='high'?'red':disease.severity==='medium'?'orange':'green'}`}>{disease.severity}</span>
						)}
						{disease.season && (<span className="badge">{disease.season}</span>)}
						{disease.region && (<span className="badge">{disease.region}</span>)}
					</div>

					<div className="kv">
						<label>Crop</label>
						<div>{disease.cropName}</div>
						<label>Disease</label>
						<div>{disease.diseaseName}</div>
					</div>
					<div className="section">
						<h3>Symptoms</h3>
						<ul>
							{disease.symptoms.map((s,i)=>(<li key={i}>{s}</li>))}
						</ul>
					</div>
					<div className="section">
						<h3>Organic Treatment</h3>
						<ul>
							{disease.organicTreatment.map((s,i)=>(<li key={i}>{s}</li>))}
						</ul>
					</div>
					<div className="section">
						<h3>Chemical Treatment</h3>
						<ul>
							{disease.chemicalTreatment.map((s,i)=>(<li key={i}>{s}</li>))}
						</ul>
					</div>
					<div className="section">
						<h3>Prevention Tips</h3>
						<ul>
							{disease.preventionTips.map((s,i)=>(<li key={i}>{s}</li>))}
						</ul>
					</div>
				</div>
			</div>
		</div>
	)
}



