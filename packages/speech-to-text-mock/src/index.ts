/**
 * Mock Speech-to-Text - outputs raw text only
 * Semantic normalization handles all extraction (facts + child names)
 */

import { SAMPLE_UTTERANCES, getRandomUtterance } from './sample-utterances';

export interface TranscriptionResult {
  text: string;
  timestamp: Date;
}

export class MockSTT {
  /**
   * Simulate speech-to-text transcription
   * Returns raw text only - no semantic processing
   */
  async transcribe(options: { index?: number; delay?: number } = {}): Promise<TranscriptionResult> {
    const { index, delay = 0 } = options;

    if (delay > 0) {
      await new Promise(resolve => setTimeout(resolve, delay));
    }

    let text: string;
    if (index !== undefined) {
      if (index < 0 || index >= SAMPLE_UTTERANCES.length) {
        throw new Error(`Index ${index} out of bounds. Valid: 0-${SAMPLE_UTTERANCES.length - 1}`);
      }
      text = SAMPLE_UTTERANCES[index];
    } else {
      text = getRandomUtterance();
    }

    return { text, timestamp: new Date() };
  }

  getUtteranceCount(): number {
    return SAMPLE_UTTERANCES.length;
  }

  getAllUtterances(): string[] {
    return [...SAMPLE_UTTERANCES];
  }
}

export { SAMPLE_UTTERANCES, getRandomUtterance } from './sample-utterances';
