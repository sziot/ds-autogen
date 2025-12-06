import { DiffLine, DiffChunk } from '../types';
import * as diff from 'diff';

export function generateDiff(oldText: string, newText: string): DiffChunk[] {
  const diffResult = diff.diffLines(oldText, newText);
  const chunks: DiffChunk[] = [];
  let oldLineNumber = 1;
  let newLineNumber = 1;
  let currentChunk: DiffChunk | null = null;

  diffResult.forEach((part) => {
    const lines = part.value.split('\n');
    
    lines.forEach((line, lineIndex) => {
      if (line === '' && lineIndex === lines.length - 1) return;

      if (!currentChunk) {
        currentChunk = {
          oldStart: oldLineNumber,
          newStart: newLineNumber,
          lines: [],
        };
      }

      const diffLine: DiffLine = {
        type: part.added ? 'added' : part.removed ? 'removed' : 'unchanged',
        content: line,
        lineNumber: newLineNumber,
        oldLineNumber: part.removed ? undefined : oldLineNumber,
        newLineNumber: part.added ? undefined : newLineNumber,
      };

      currentChunk.lines.push(diffLine);

      if (part.added) {
        newLineNumber++;
      } else if (part.removed) {
        oldLineNumber++;
      } else {
        oldLineNumber++;
        newLineNumber++;
      }

      // 每10行或者类型变化时开始新的chunk
      if (
        currentChunk.lines.length >= 10 ||
        (currentChunk.lines.length > 0 && 
         currentChunk.lines[currentChunk.lines.length - 1].type !== diffLine.type)
      ) {
        chunks.push(currentChunk);
        currentChunk = null;
      }
    });
  });

  if (currentChunk) {
    chunks.push(currentChunk);
  }

  return chunks;
}

export function getDiffStats(oldText: string, newText: string) {
  const diffResult = diff.diffLines(oldText, newText);
  
  const stats = {
    additions: 0,
    deletions: 0,
    changes: 0,
  };

  diffResult.forEach(part => {
    if (part.added) {
      stats.additions += part.count || 0;
    } else if (part.removed) {
      stats.deletions += part.count || 0;
    }
  });

  stats.changes = stats.additions + stats.deletions;
  return stats;
}