import { useCallback, useEffect, useMemo, useState } from 'react'
import type { Note } from '../types/note'

const STORAGE_KEY = 'md-notes-desktop-notes'

function generateId(): string {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 9)}`
}

function getFirstLine(text: string): string {
  return text.split('\n')[0].replace(/^#+\s*/, '').trim() || '无标题笔记'
}

function loadNotes(): Note[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw) as Note[]
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function saveNotes(notes: Note[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(notes))
  } catch (e) {
    console.error('Failed to save notes to LocalStorage:', e)
  }
}

export function useNotes() {
  const [notes, setNotes] = useState<Note[]>([])
  const [initialized, setInitialized] = useState(false)

  useEffect(() => {
    setNotes(loadNotes())
    setInitialized(true)
  }, [])

  useEffect(() => {
    if (initialized) {
      saveNotes(notes)
    }
  }, [notes, initialized])

  const createNote = useCallback((content = '') => {
    const now = Date.now()
    const newNote: Note = {
      id: generateId(),
      title: getFirstLine(content) || '新笔记',
      content,
      createdAt: now,
      updatedAt: now,
    }
    setNotes((prev) => [newNote, ...prev])
    return newNote.id
  }, [])

  const updateNote = useCallback((id: string, content: string) => {
    setNotes((prev) =>
      prev.map((note) =>
        note.id === id
          ? { ...note, content, title: getFirstLine(content), updatedAt: Date.now() }
          : note,
      ),
    )
  }, [])

  const deleteNote = useCallback((id: string) => {
    setNotes((prev) => prev.filter((note) => note.id !== id))
  }, [])

  const searchNotes = useCallback(
    (query: string) => {
      const q = query.trim().toLowerCase()
      if (!q) return notes
      return notes.filter(
        (note) =>
          note.title.toLowerCase().includes(q) || note.content.toLowerCase().includes(q),
      )
    },
    [notes],
  )

  const sortedNotes = useMemo(
    () => [...notes].sort((a, b) => b.updatedAt - a.updatedAt),
    [notes],
  )

  return {
    notes: sortedNotes,
    initialized,
    createNote,
    updateNote,
    deleteNote,
    searchNotes,
  }
}
