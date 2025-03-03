interface QuickRepliesProps {
  replies: string[];
  onReplyClick: (reply: string) => void;
}

export default function QuickReplies({ replies, onReplyClick }: QuickRepliesProps) {
  if (!replies || replies.length === 0) return null;
  
  return (
    <div className="flex flex-wrap mt-4 mb-8">
      {replies.map((reply, index) => (
        <button
          key={`${reply}-${index}`}
          className="quick-reply"
          onClick={() => onReplyClick(reply)}
        >
          {reply}
        </button>
      ))}
    </div>
  );
} 