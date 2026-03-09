import { renderHook, act } from '@testing-library/react';
import { useTodos } from './useTodos';
import * as migration from '@/lib/migration';

// Mock the migration module
jest.mock('@/lib/migration', () => ({
  loadTodos: jest.fn(),
  saveTodos: jest.fn(),
}));

// Mock nanoid
let mockIdCounter = 0;
jest.mock('nanoid', () => ({
  nanoid: jest.fn(() => `test-id-${mockIdCounter++}`),
}));

describe('useTodos', () => {
  const mockLoadTodos = migration.loadTodos as jest.MockedFunction<typeof migration.loadTodos>;
  const mockSaveTodos = migration.saveTodos as jest.MockedFunction<typeof migration.saveTodos>;

  beforeEach(() => {
    jest.clearAllMocks();
    mockLoadTodos.mockReturnValue([]);
    mockIdCounter = 0;
  });

  describe('初期化', () => {
    it('マウント時にlocalStorageからタスクを読み込む', () => {
      const initialTodos = [
        {
          id: '1',
          text: 'Test todo',
          completed: false,
          priority: 'medium' as const,
          dueDate: null,
          order: 0,
          createdAt: Date.now(),
          updatedAt: Date.now(),
        },
      ];
      mockLoadTodos.mockReturnValue(initialTodos);

      const { result } = renderHook(() => useTodos());

      expect(mockLoadTodos).toHaveBeenCalledTimes(1);
      expect(result.current.todos).toEqual(initialTodos);
      expect(result.current.isInitialized).toBe(true);
    });

    it('初期状態では空の配列を返す', () => {
      const { result } = renderHook(() => useTodos());

      expect(result.current.todos).toEqual([]);
      expect(result.current.isInitialized).toBe(true);
    });
  });

  describe('addTodo', () => {
    it('新しいタスクを追加できる', () => {
      const { result } = renderHook(() => useTodos());

      act(() => {
        result.current.addTodo('新しいタスク');
      });

      expect(result.current.todos).toHaveLength(1);
      expect(result.current.todos[0]).toMatchObject({
        id: 'test-id-0',
        text: '新しいタスク',
        completed: false,
        priority: 'medium',
        dueDate: null,
        order: 0,
      });
      expect(mockSaveTodos).toHaveBeenCalledWith(result.current.todos);
    });

    it('優先度を指定してタスクを追加できる', () => {
      const { result } = renderHook(() => useTodos());

      act(() => {
        result.current.addTodo('高優先度タスク', 'high');
      });

      expect(result.current.todos[0].priority).toBe('high');
    });

    it('追加したタスクにタイムスタンプが設定される', () => {
      const { result } = renderHook(() => useTodos());
      const beforeTime = Date.now();

      act(() => {
        result.current.addTodo('タイムスタンプテスト');
      });

      const afterTime = Date.now();
      const todo = result.current.todos[0];

      expect(todo.createdAt).toBeGreaterThanOrEqual(beforeTime);
      expect(todo.createdAt).toBeLessThanOrEqual(afterTime);
      expect(todo.updatedAt).toBeGreaterThanOrEqual(beforeTime);
      expect(todo.updatedAt).toBeLessThanOrEqual(afterTime);
    });
  });

  describe('updateTodo', () => {
    it('タスクを更新できる', () => {
      mockLoadTodos.mockReturnValue([
        {
          id: '1',
          text: '元のテキスト',
          completed: false,
          priority: 'medium',
          dueDate: null,
          order: 0,
          createdAt: 1000,
          updatedAt: 1000,
        },
      ]);

      const { result } = renderHook(() => useTodos());

      act(() => {
        result.current.updateTodo('1', { text: '更新されたテキスト', priority: 'high' });
      });

      expect(result.current.todos[0].text).toBe('更新されたテキスト');
      expect(result.current.todos[0].priority).toBe('high');
      expect(result.current.todos[0].updatedAt).toBeGreaterThan(1000);
      expect(mockSaveTodos).toHaveBeenCalled();
    });

    it('存在しないIDの場合は何も変更しない', () => {
      mockLoadTodos.mockReturnValue([
        {
          id: '1',
          text: '元のテキスト',
          completed: false,
          priority: 'medium',
          dueDate: null,
          order: 0,
          createdAt: 1000,
          updatedAt: 1000,
        },
      ]);

      const { result } = renderHook(() => useTodos());
      const originalTodos = [...result.current.todos];

      act(() => {
        result.current.updateTodo('999', { text: '更新されたテキスト' });
      });

      expect(result.current.todos[0].text).toBe('元のテキスト');
    });
  });

  describe('deleteTodo', () => {
    it('タスクを削除できる', () => {
      mockLoadTodos.mockReturnValue([
        {
          id: '1',
          text: 'タスク1',
          completed: false,
          priority: 'medium',
          dueDate: null,
          order: 0,
          createdAt: 1000,
          updatedAt: 1000,
        },
        {
          id: '2',
          text: 'タスク2',
          completed: false,
          priority: 'medium',
          dueDate: null,
          order: 1,
          createdAt: 1000,
          updatedAt: 1000,
        },
      ]);

      const { result } = renderHook(() => useTodos());

      act(() => {
        result.current.deleteTodo('1');
      });

      expect(result.current.todos).toHaveLength(1);
      expect(result.current.todos[0].id).toBe('2');
      expect(mockSaveTodos).toHaveBeenCalled();
    });

    it('存在しないIDの場合は何も削除しない', () => {
      mockLoadTodos.mockReturnValue([
        {
          id: '1',
          text: 'タスク1',
          completed: false,
          priority: 'medium',
          dueDate: null,
          order: 0,
          createdAt: 1000,
          updatedAt: 1000,
        },
      ]);

      const { result } = renderHook(() => useTodos());

      act(() => {
        result.current.deleteTodo('999');
      });

      expect(result.current.todos).toHaveLength(1);
    });
  });

  describe('toggleTodo', () => {
    it('完了状態を切り替えられる', () => {
      mockLoadTodos.mockReturnValue([
        {
          id: '1',
          text: 'タスク1',
          completed: false,
          priority: 'medium',
          dueDate: null,
          order: 0,
          createdAt: 1000,
          updatedAt: 1000,
        },
      ]);

      const { result } = renderHook(() => useTodos());

      act(() => {
        result.current.toggleTodo('1');
      });

      expect(result.current.todos[0].completed).toBe(true);
      expect(result.current.todos[0].updatedAt).toBeGreaterThan(1000);

      act(() => {
        result.current.toggleTodo('1');
      });

      expect(result.current.todos[0].completed).toBe(false);
      expect(mockSaveTodos).toHaveBeenCalled();
    });
  });

  describe('updateTodoText', () => {
    it('タスクのテキストを更新できる', () => {
      mockLoadTodos.mockReturnValue([
        {
          id: '1',
          text: '元のテキスト',
          completed: false,
          priority: 'medium',
          dueDate: null,
          order: 0,
          createdAt: 1000,
          updatedAt: 1000,
        },
      ]);

      const { result } = renderHook(() => useTodos());

      act(() => {
        result.current.updateTodoText('1', '新しいテキスト');
      });

      expect(result.current.todos[0].text).toBe('新しいテキスト');
      expect(mockSaveTodos).toHaveBeenCalled();
    });
  });

  describe('updateTodoPriority', () => {
    it('タスクの優先度を更新できる', () => {
      mockLoadTodos.mockReturnValue([
        {
          id: '1',
          text: 'タスク',
          completed: false,
          priority: 'medium',
          dueDate: null,
          order: 0,
          createdAt: 1000,
          updatedAt: 1000,
        },
      ]);

      const { result } = renderHook(() => useTodos());

      act(() => {
        result.current.updateTodoPriority('1', 'high');
      });

      expect(result.current.todos[0].priority).toBe('high');
      expect(mockSaveTodos).toHaveBeenCalled();
    });
  });

  describe('updateTodoDueDate', () => {
    it('タスクの期限を更新できる', () => {
      mockLoadTodos.mockReturnValue([
        {
          id: '1',
          text: 'タスク',
          completed: false,
          priority: 'medium',
          dueDate: null,
          order: 0,
          createdAt: 1000,
          updatedAt: 1000,
        },
      ]);

      const { result } = renderHook(() => useTodos());
      const dueDate = Date.now() + 86400000; // 1日後

      act(() => {
        result.current.updateTodoDueDate('1', dueDate);
      });

      expect(result.current.todos[0].dueDate).toBe(dueDate);
      expect(mockSaveTodos).toHaveBeenCalled();
    });

    it('期限をnullに設定できる', () => {
      mockLoadTodos.mockReturnValue([
        {
          id: '1',
          text: 'タスク',
          completed: false,
          priority: 'medium',
          dueDate: Date.now(),
          order: 0,
          createdAt: 1000,
          updatedAt: 1000,
        },
      ]);

      const { result } = renderHook(() => useTodos());

      act(() => {
        result.current.updateTodoDueDate('1', null);
      });

      expect(result.current.todos[0].dueDate).toBeNull();
      expect(mockSaveTodos).toHaveBeenCalled();
    });
  });

  describe('reorderTodos', () => {
    it('タスクを並び替えできる', () => {
      mockLoadTodos.mockReturnValue([
        {
          id: '1',
          text: 'タスク1',
          completed: false,
          priority: 'medium',
          dueDate: null,
          order: 0,
          createdAt: 1000,
          updatedAt: 1000,
        },
        {
          id: '2',
          text: 'タスク2',
          completed: false,
          priority: 'medium',
          dueDate: null,
          order: 1,
          createdAt: 1000,
          updatedAt: 1000,
        },
        {
          id: '3',
          text: 'タスク3',
          completed: false,
          priority: 'medium',
          dueDate: null,
          order: 2,
          createdAt: 1000,
          updatedAt: 1000,
        },
      ]);

      const { result } = renderHook(() => useTodos());

      act(() => {
        result.current.reorderTodos('1', '3'); // タスク1をタスク3の位置に移動
      });

      expect(result.current.todos[0].id).toBe('2');
      expect(result.current.todos[1].id).toBe('3');
      expect(result.current.todos[2].id).toBe('1');

      // orderフィールドが正しく更新されているか確認
      expect(result.current.todos[0].order).toBe(0);
      expect(result.current.todos[1].order).toBe(1);
      expect(result.current.todos[2].order).toBe(2);

      expect(mockSaveTodos).toHaveBeenCalled();
    });

    it('存在しないIDの場合は何も変更しない', () => {
      mockLoadTodos.mockReturnValue([
        {
          id: '1',
          text: 'タスク1',
          completed: false,
          priority: 'medium',
          dueDate: null,
          order: 0,
          createdAt: 1000,
          updatedAt: 1000,
        },
        {
          id: '2',
          text: 'タスク2',
          completed: false,
          priority: 'medium',
          dueDate: null,
          order: 1,
          createdAt: 1000,
          updatedAt: 1000,
        },
      ]);

      const { result } = renderHook(() => useTodos());

      act(() => {
        result.current.reorderTodos('999', '2');
      });

      expect(result.current.todos[0].id).toBe('1');
      expect(result.current.todos[1].id).toBe('2');
    });
  });

  describe('複数の操作の組み合わせ', () => {
    it('タスクの追加、更新、削除が連続して正しく動作する', () => {
      const { result } = renderHook(() => useTodos());

      // タスクを3つ追加
      act(() => {
        result.current.addTodo('タスク1', 'high');
      });

      act(() => {
        result.current.addTodo('タスク2', 'medium');
      });

      act(() => {
        result.current.addTodo('タスク3', 'low');
      });

      expect(result.current.todos).toHaveLength(3);

      // 2番目のタスクを完了
      act(() => {
        result.current.toggleTodo(result.current.todos[1].id);
      });

      expect(result.current.todos[1].completed).toBe(true);

      // 1番目のタスクを削除
      act(() => {
        result.current.deleteTodo(result.current.todos[0].id);
      });

      expect(result.current.todos).toHaveLength(2);
      expect(result.current.todos[0].text).toBe('タスク2');
      expect(result.current.todos[0].completed).toBe(true);
    });
  });
});
