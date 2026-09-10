import { useEffect, useMemo, useRef, useState } from 'react'
import { MarkdownPreview } from './components/MarkdownPreview'
import { useNotes } from './hooks/useNotes'
import type { Note } from './types/note'

function formatDate(ts: number): string {
  const d = new Date(ts)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

function getNoteSummary(content: string): string {
  return content.slice(0, 80).replace(/\n/g, ' ') || '无内容'
}

// 从草稿首行推导标题（用于编辑器头部即时显示，无需等待落盘）
function getLiveTitle(content: string): string {
  return content.split('\n')[0].replace(/^#+\s*/, '').trim() || '无标题笔记'
}

export default function App() {
  const { notes, initialized, createNote, updateNote, deleteNote, searchNotes } = useNotes()
  const [activeId, setActiveId] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  // 编辑器即时草稿：输入即更新，预览直接读它，保证零延迟同步
  const [draft, setDraft] = useState('')
  // 保存状态指示：'editing' = 正在输入未落盘，'saved' = 已写入 LocalStorage
  const [saveStatus, setSaveStatus] = useState<'editing' | 'saved'>('saved')
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const filteredNotes = useMemo(() => searchNotes(query), [searchNotes, query])

  const activeNote = useMemo(
    () => notes.find((n) => n.id === activeId) || null,
    [notes, activeId],
  )

  // 切换笔记时：加载该笔记内容到草稿，并清除未完成的保存定时器（避免误写回上一篇）
  useEffect(() => {
    if (saveTimer.current) {
      clearTimeout(saveTimer.current)
      saveTimer.current = null
    }
    if (activeId) {
      const n = notes.find((x) => x.id === activeId)
      setDraft(n ? n.content : '')
      setSaveStatus('saved')
    } else {
      setDraft('')
    }
    // 仅依赖 activeId：切换笔记才重置草稿，输入过程中不回灌已持久化内容（防止光标跳动）
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeId])

  // 首次加载自动选中第一篇笔记
  useEffect(() => {
    if (initialized && !activeId && notes.length > 0) {
      setActiveId(notes[0].id)
    }
  }, [initialized, notes, activeId])

  const handleCreate = () => {
    // 新建前先 flush 当前草稿，避免覆盖
    if (saveTimer.current) {
      clearTimeout(saveTimer.current)
      saveTimer.current = null
    }
    const id = createNote('# 新笔记\n\n开始书写...')
    setActiveId(id)
    setQuery('')
    setDraft('# 新笔记\n\n开始书写...')
    setSaveStatus('saved')
    setTimeout(() => textareaRef.current?.focus(), 0)
  }

  const handleDelete = (note: Note, e: React.MouseEvent) => {
    e.stopPropagation()
    if (confirm(`确定要删除笔记 "${note.title}" 吗？`)) {
      if (saveTimer.current) {
        clearTimeout(saveTimer.current)
        saveTimer.current = null
      }
      deleteNote(note.id)
      if (activeId === note.id) {
        setActiveId(null)
      }
    }
  }

  // 核心：监听编辑器输入变化 —— 即时更新草稿（预览同步），并防抖落盘
  const handleChange = (value: string) => {
    setDraft(value) // 这一步让右侧预览实时刷新
    setSaveStatus('editing')
    if (saveTimer.current) clearTimeout(saveTimer.current)
    if (activeId) {
      saveTimer.current = setTimeout(() => {
        updateNote(activeId, value)
        setSaveStatus('saved')
        saveTimer.current = null
      }, 300)
    }
  }

  const liveTitle = activeNote ? getLiveTitle(draft) : ''
  const charCount = draft.length

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50 text-slate-800">
      {/* Sidebar */}
      <aside className="w-72 flex-shrink-0 flex flex-col border-r border-slate-200 bg-white">
        <div className="p-4 border-b border-slate-200">
          <div className="flex items-center justify-between mb-3">
            <h1 className="text-lg font-semibold text-slate-900">Markdown 笔记</h1>
            <button
              onClick={handleCreate}
              className="px-3 py-1.5 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors"
            >
              新建
            </button>
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="搜索笔记..."
            className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>

        <div className="flex-1 overflow-y-auto">
          {filteredNotes.length === 0 ? (
            <div className="p-6 text-center text-sm text-slate-400">
              {query ? '没有匹配的笔记' : '还没有笔记，点击上方“新建”开始'}
            </div>
          ) : (
            <ul className="divide-y divide-slate-100">
              {filteredNotes.map((note) => (
                <li
                  key={note.id}
                  onClick={() => setActiveId(note.id)}
                  className={`group cursor-pointer p-4 transition-colors hover:bg-slate-50 ${
                    activeId === note.id ? 'bg-indigo-50 border-r-4 border-indigo-600' : ''
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0 flex-1">
                      <h3 className="text-sm font-medium text-slate-900 truncate">
                        {note.title}
                      </h3>
                      <p className="mt-1 text-xs text-slate-500 truncate">
                        {getNoteSummary(note.content)}
                      </p>
                      <p className="mt-1.5 text-[11px] text-slate-400">
                        {formatDate(note.updatedAt)}
                      </p>
                    </div>
                    <button
                      onClick={(e) => handleDelete(note, e)}
                      className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-red-600 transition-opacity"
                      title="删除"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </aside>

      {/* Editor */}
      <main className="flex-1 flex flex-col min-w-0 border-r border-slate-200 bg-white">
        {activeNote ? (
          <>
            <div className="px-4 py-3 border-b border-slate-200 bg-slate-50 flex items-center justify-between gap-3">
              <h2 className="text-sm font-medium text-slate-700 truncate">{liveTitle}</h2>
              <div className="flex items-center gap-3 text-[11px] text-slate-400 whitespace-nowrap">
                <span className="tabular-nums">{charCount} 字</span>
                {saveStatus === 'editing' ? (
                  <span className="flex items-center gap-1 text-amber-500">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
                    编辑中…
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-emerald-500">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    已保存
                  </span>
                )}
              </div>
            </div>
            <textarea
              ref={textareaRef}
              value={draft}
              onChange={(e) => handleChange(e.target.value)}
              className="flex-1 w-full p-6 resize-none focus:outline-none font-mono text-[15px] leading-relaxed text-slate-800"
              placeholder="在此输入 Markdown..."
              spellCheck={false}
            />
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-slate-400">
            <div className="text-center">
              <p className="mb-3">选择或创建一个笔记开始编辑</p>
              <button
                onClick={handleCreate}
                className="px-4 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 hover:bg-indigo-100 rounded-lg transition-colors"
              >
                新建笔记
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Preview */}
      <section className="flex-1 min-w-0 bg-slate-50">
        {activeNote ? (
          <MarkdownPreview content={draft} />
        ) : (
          <div className="h-full flex items-center justify-center text-slate-400">
            预览区域
          </div>
        )}
      </section>
    </div>
  )
}
