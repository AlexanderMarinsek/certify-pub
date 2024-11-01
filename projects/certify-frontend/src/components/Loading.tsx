export default function Loading({ visible }: { visible: boolean }) {
  return (
    <>
      {visible && (
        <>
          <div className="w-5 h-5 border-4 border-t-gray-700 border-gray-300 rounded-full animate-spin"></div>
        </>
      )}
    </>
  )
}
