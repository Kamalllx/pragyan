import {createContext, useContext} from 'react';

/** The few words the motion library itself puts on screen, per narration language. */
const LABELS = {
	en: {definition: 'Definition', analogy: 'Think of it like', takeaways: 'Key takeaways', steps: 'Step by step', answer: 'Answer', timeline: 'Timeline', quiz: 'Check yourself', think: 'Pause & think', why: 'Why', verdict: 'Verdict', unit: 'Unit'},
	hi: {definition: 'परिभाषा', analogy: 'इसे ऐसे समझें', takeaways: 'मुख्य बातें', steps: 'चरण दर चरण', answer: 'उत्तर', timeline: 'समयरेखा', quiz: 'खुद को परखें', think: 'रुकें और सोचें', why: 'क्यों', verdict: 'निष्कर्ष', unit: 'इकाई'},
	es: {definition: 'Definición', analogy: 'Piénsalo así', takeaways: 'Ideas clave', steps: 'Paso a paso', answer: 'Respuesta', timeline: 'Cronología', quiz: 'Ponte a prueba', think: 'Pausa y piensa', why: 'Por qué', verdict: 'Veredicto', unit: 'Unidad'},
	fr: {definition: 'Définition', analogy: 'Imagine-le ainsi', takeaways: 'À retenir', steps: 'Étape par étape', answer: 'Réponse', timeline: 'Chronologie', quiz: 'Teste-toi', think: 'Pause et réflexion', why: 'Pourquoi', verdict: 'Verdict', unit: 'Unité'},
} as const;

export type LabelKey = keyof (typeof LABELS)['en'];
export const LangContext = createContext<string>('en');
export const useLabel = () => {
	const lang = useContext(LangContext);
	const table = (LABELS as Record<string, Record<LabelKey, string>>)[lang] ?? LABELS.en;
	return (k: LabelKey) => table[k] ?? LABELS.en[k];
};
