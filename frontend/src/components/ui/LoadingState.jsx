import Card from "./Card";

function LoadingState({ message = "Loading..." }) {
  return (
    <Card className="p-6">
      <div className="flex items-center gap-3">
        <div
          className="h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-slate-900"
          aria-hidden="true"
        />

        <p className="text-sm text-slate-500">
          {message}
        </p>
      </div>
    </Card>
  );
}

export default LoadingState;