import ChatBoxSuspense from "@/components/ChatBox";

export default function Home() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-base-100 p-4 sm:p-8">
      <h1 className="text-3xl font-bold mb-6 text-center">AI Knowledge Assistant</h1>
      <ChatBoxSuspense />
    </main>
  );
}
