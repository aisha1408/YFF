import raw from '../resources/diseases.json'
import type { Disease } from './types'

type Loose = any

function toArray(value: unknown): string[]{
	if(Array.isArray(value)) return value as string[]
	if(typeof value === 'string' && value.trim().length>0) return value.split(/\s*;\s*|\n+/).filter(Boolean)
	return []
}

export function getDiseases(): Disease[]{
	const items: Loose[] = raw as Loose[]
	return items.map((it, idx) => {
		return {
			id: (it.id ?? String(idx+1)) as string,
			cropName: it.cropName ?? '',
			diseaseName: it.diseaseName ?? '',
			symptoms: toArray(it.symptoms),
			organicTreatment: toArray(it.organicTreatment),
			chemicalTreatment: toArray(it.chemicalTreatment),
			preventionTips: toArray(it.preventionTips),
			severity: it.severity,
			region: it.region,
			season: it.season,
			imageURL: it.imageURL ?? '/assets/placeholder.jpg',
		}
	})
}


