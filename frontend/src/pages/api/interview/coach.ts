import { NextApiRequest, NextApiResponse } from 'next';
import { GoogleGenerativeAI } from '@google/generative-ai';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { question, answer, resumeAnalysis } = req.body;
    
    if (!question || !answer) {
      return res.status(400).json({ error: 'Question and answer are required' });
    }

    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
    const model = genAI.getGenerativeModel({ model: "gemini-2.5-pro" });
    
    const prompt = `You are an expert interview coach. Analyze this interview response and provide feedback:
    
    Question: ${question}
    
    Candidate Answer: ${answer}
    
    Resume Analysis: ${JSON.stringify(resumeAnalysis)}
    
    Please provide feedback on:
    1. Content quality and relevance
    2. Communication skills
    3. Technical accuracy (if applicable)
    4. Areas for improvement
    5. Suggestions for better answers
    
    Format your response as JSON with these sections.`;
    
    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();
    
    // Parse the JSON response
    let feedback;
    try {
      feedback = JSON.parse(text);
    } catch (parseError) {
      // If it's not valid JSON, try to extract JSON from the text
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        feedback = JSON.parse(jsonMatch[0]);
      } else {
        throw new Error('Failed to parse AI response');
      }
    }
    
    res.status(200).json({ 
      success: true,
      feedback: feedback,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Interview coaching error:', error);
    res.status(500).json({ 
      error: 'Coaching failed',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}

export const config = {
  api: {
    bodyParser: {
      sizeLimit: '10mb',
    },
  },
};