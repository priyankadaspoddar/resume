import { NextRequest, NextResponse } from 'next/server';

export const config = {
  runtime: 'edge',
};

export default async function handler(req: NextRequest) {
  if (req.method !== 'POST') {
    return NextResponse.json({ error: 'Method not allowed' }, { status: 405 });
  }

  try {
    const body = await req.json();
    const { question, answer, resumeAnalysis } = body;
    
    if (!question || !answer) {
      return NextResponse.json({ error: 'Question and answer are required' }, { status: 400 });
    }

    // For Vercel Edge Runtime, we need to use fetch instead of Google's library
    const response = await fetch('https://generativelanguage.googleapis.com/v1/models/gemini-2.5-pro:generateContent', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.GEMINI_API_KEY}`,
      },
      body: JSON.stringify({
        contents: [{
          parts: [{
            text: `You are an expert interview coach. Analyze this interview response and provide feedback:
            
            Question: ${question}
            
            Candidate Answer: ${answer}
            
            Resume Analysis: ${JSON.stringify(resumeAnalysis)}
            
            Please provide feedback on:
            1. Content quality and relevance
            2. Communication skills
            3. Technical accuracy (if applicable)
            4. Areas for improvement
            5. Suggestions for better answers
            
            Format your response as JSON with these sections.`
          }]
        }]
      })
    });

    if (!response.ok) {
      throw new Error(`Gemini API error: ${response.status}`);
    }

    const data = await response.json();
    const text = data.candidates[0].content.parts[0].text;
    
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
    
    return NextResponse.json({ 
      success: true,
      feedback: feedback,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Interview coaching error:', error);
    return NextResponse.json({ 
      error: 'Coaching failed',
      message: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}