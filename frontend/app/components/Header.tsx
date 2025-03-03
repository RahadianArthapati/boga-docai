import { MdOutlineDarkMode, MdDeleteOutline, MdBugReport } from 'react-icons/md';
import Link from 'next/link';

interface HeaderProps {
  clearChat: () => void;
  toggleTheme: () => void;
}

export default function Header({ clearChat, toggleTheme }: HeaderProps) {
  return (
    <div className="flex items-center justify-between p-4 bg-white rounded-chat shadow-sm mb-4">
      <div className="flex items-center">
        <div className="w-12 h-12 rounded-full bg-primary flex items-center justify-center text-white font-bold text-lg mr-4">
          AI
        </div>
        <div>
          <h1 className="font-bold text-lg">AI Assistant</h1>
          <p className="text-gray-500 text-sm">Online</p>
        </div>
      </div>
      <div className="flex items-center">
        <Link
          href="/debug"
          className="p-2 rounded-full hover:bg-gray-100 transition-colors"
          aria-label="Debug"
        >
          <MdBugReport className="text-gray-500 text-xl" />
        </Link>
        <button
          onClick={toggleTheme}
          className="p-2 rounded-full hover:bg-gray-100 transition-colors ml-2"
          aria-label="Toggle theme"
        >
          <MdOutlineDarkMode className="text-gray-500 text-xl" />
        </button>
        <button
          onClick={clearChat}
          className="p-2 rounded-full hover:bg-gray-100 transition-colors ml-2"
          aria-label="Clear chat"
        >
          <MdDeleteOutline className="text-gray-500 text-xl" />
        </button>
      </div>
    </div>
  );
} 