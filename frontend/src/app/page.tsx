/**
 * =============================================================================
 * Projet: Doctis AI
 * Auteurs: Adam Beloucif & Amina Medjdoub
 * Description: Interface principale de pré-diagnostic médical
 * =============================================================================
 */

"use client";

import { useState } from "react";

// Types
interface PathologyMatch {
  id: string;
  name: string;
  confidence_score: number;
  severity_level: number;
  urgency: string;
  advice: string;
  specialist: string;
}

interface DiagnosisResponse {
  success: boolean;
  matched: boolean;
  pathology: PathologyMatch | null;
  ai_response: string;
  disclaimer: string;
  authors: string[];
}

// Configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [symptoms, setSymptoms] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<DiagnosisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (symptoms.trim().length < 10) {
      setError("Veuillez décrire vos symptômes plus en détail (minimum 10 caractères).");
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/diagnose`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ symptoms: symptoms.trim() }),
      });

      if (!response.ok) {
        throw new Error(`Erreur serveur: ${response.status}`);
      }

      const data: DiagnosisResponse = await response.json();
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Une erreur est survenue lors de l'analyse."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const getSeverityColor = (level: number): string => {
    const colors: Record<number, string> = {
      1: "bg-green-500",
      2: "bg-lime-500",
      3: "bg-yellow-500",
      4: "bg-orange-500",
      5: "bg-red-500",
    };
    return colors[level] || "bg-gray-500";
  };

  const getSeverityLabel = (level: number): string => {
    const labels: Record<number, string> = {
      1: "Très faible",
      2: "Faible",
      3: "Modérée",
      4: "Élevée",
      5: "Urgente",
    };
    return labels[level] || "Inconnue";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-blue-100">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center">
              <svg
                className="w-7 h-7 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Doctis AI</h1>
              <p className="text-sm text-gray-500">Assistant de pré-diagnostic médical</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Introduction */}
        <div className="text-center mb-10">
          <h2 className="text-3xl font-semibold text-gray-800 mb-3">
            Décrivez vos symptômes
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Notre IA analyse vos symptômes et vous oriente vers les soins appropriés.
            Ce service ne remplace pas une consultation médicale.
          </p>
        </div>

        {/* Formulaire */}
        <form onSubmit={handleSubmit} className="mb-8">
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-blue-100">
            <label
              htmlFor="symptoms"
              className="block text-sm font-medium text-gray-700 mb-3"
            >
              Vos symptômes
            </label>
            <textarea
              id="symptoms"
              value={symptoms}
              onChange={(e) => setSymptoms(e.target.value)}
              placeholder="Ex: J'ai mal au ventre en bas à droite depuis ce matin, avec des nausées et une légère fièvre..."
              className="w-full h-32 px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-gray-700 placeholder-gray-400"
              disabled={isLoading}
            />
            <div className="flex items-center justify-between mt-4">
              <span className="text-xs text-gray-400">
                {symptoms.length} caractères (min. 10)
              </span>
              <button
                type="submit"
                disabled={isLoading || symptoms.trim().length < 10}
                className="px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-xl hover:from-blue-600 hover:to-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2"
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    Analyse en cours...
                  </>
                ) : (
                  <>
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                      />
                    </svg>
                    Analyser mes symptômes
                  </>
                )}
              </button>
            </div>
          </div>
        </form>

        {/* Erreur */}
        {error && (
          <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 flex items-start gap-3">
            <svg
              className="w-5 h-5 mt-0.5 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>{error}</span>
          </div>
        )}

        {/* Résultat */}
        {result && (
          <div className="space-y-6">
            {/* Carte de Diagnostic */}
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden border border-blue-100">
              {/* En-tête */}
              <div className={`px-6 py-4 ${result.matched ? 'bg-gradient-to-r from-blue-500 to-cyan-500' : 'bg-gray-500'} text-white`}>
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">
                    {result.matched ? "Pré-diagnostic" : "Analyse incomplète"}
                  </h3>
                  {result.pathology && (
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getSeverityColor(result.pathology.severity_level)} bg-opacity-80`}>
                      Gravité: {getSeverityLabel(result.pathology.severity_level)}
                    </span>
                  )}
                </div>
              </div>

              {/* Contenu */}
              <div className="p-6">
                {result.matched && result.pathology ? (
                  <>
                    {/* Nom de la pathologie */}
                    <div className="mb-6">
                      <h4 className="text-2xl font-bold text-gray-800 mb-2">
                        {result.pathology.name}
                      </h4>
                      <span className="inline-block px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm font-medium">
                        {result.pathology.urgency}
                      </span>
                    </div>

                    {/* Barre de confiance */}
                    <div className="mb-6">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-600">
                          Confiance de l'IA
                        </span>
                        <span className="text-sm font-bold text-blue-600">
                          {Math.round(result.pathology.confidence_score * 100)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full transition-all duration-500"
                          style={{ width: `${result.pathology.confidence_score * 100}%` }}
                        />
                      </div>
                    </div>

                    {/* Spécialiste recommandé */}
                    <div className="mb-6 p-4 bg-blue-50 rounded-xl">
                      <div className="flex items-center gap-2 mb-1">
                        <svg
                          className="w-5 h-5 text-blue-600"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                          />
                        </svg>
                        <span className="text-sm font-medium text-blue-800">
                          Spécialiste recommandé
                        </span>
                      </div>
                      <p className="text-blue-700">{result.pathology.specialist}</p>
                    </div>

                    {/* Conseil */}
                    <div className="mb-6 p-4 bg-green-50 rounded-xl">
                      <div className="flex items-center gap-2 mb-1">
                        <svg
                          className="w-5 h-5 text-green-600"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                        <span className="text-sm font-medium text-green-800">
                          Conseil médical
                        </span>
                      </div>
                      <p className="text-green-700">{result.pathology.advice}</p>
                    </div>
                  </>
                ) : null}

                {/* Réponse IA */}
                <div className="p-4 bg-gray-50 rounded-xl">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
                      <svg
                        className="w-5 h-5 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                        />
                      </svg>
                    </div>
                    <span className="text-sm font-medium text-gray-700">
                      Réponse de Doctis AI
                    </span>
                  </div>
                  <p className="text-gray-700 whitespace-pre-line leading-relaxed">
                    {result.ai_response}
                  </p>
                </div>
              </div>

              {/* Disclaimer */}
              <div className="px-6 py-4 bg-amber-50 border-t border-amber-100">
                <div className="flex items-start gap-2">
                  <svg
                    className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                  <p className="text-sm text-amber-700">
                    <strong>Avertissement :</strong> {result.disclaimer}
                  </p>
                </div>
              </div>
            </div>

            {/* Bouton Réinitialiser */}
            <div className="text-center">
              <button
                onClick={() => {
                  setResult(null);
                  setSymptoms("");
                }}
                className="px-6 py-2 text-gray-600 hover:text-gray-800 font-medium transition-colors"
              >
                ← Nouvelle analyse
              </button>
            </div>
          </div>
        )}

        {/* Exemples de symptômes */}
        {!result && (
          <div className="mt-12">
            <h3 className="text-lg font-semibold text-gray-700 mb-4 text-center">
              Exemples de descriptions
            </h3>
            <div className="grid md:grid-cols-3 gap-4">
              {[
                "J'ai mal au ventre en bas à droite et je vomis depuis ce matin, avec un peu de fièvre",
                "J'ai très mal à la tête d'un côté, je supporte plus la lumière et j'ai des nausées",
                "J'ai la diarrhée depuis 2 jours avec des crampes au ventre et je me sens très fatigué"
              ].map((example, index) => (
                <button
                  key={index}
                  onClick={() => setSymptoms(example)}
                  className="p-4 text-left bg-white rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all text-sm text-gray-600"
                >
                  "{example}"
                </button>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-auto py-8 border-t border-gray-200 bg-white">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <p className="text-gray-600 font-medium">
            Projet réalisé par <strong>Adam Beloucif</strong> & <strong>Amina Medjdoub</strong>
          </p>
          <p className="text-sm text-gray-400 mt-1">
            Doctis AI - EFREI 2025 | Module IA Générative & Data Engineering
          </p>
        </div>
      </footer>
    </div>
  );
}
