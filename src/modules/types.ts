export type Disease = {
	id: string
	cropName: string
	diseaseName: string
	symptoms: string[]
	organicTreatment: string[]
	chemicalTreatment: string[]
	preventionTips: string[]
	severity?: 'low' | 'medium' | 'high'
	region?: string
	season?: string
	imageURL: string
}


