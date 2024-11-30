export function Footer() {
  return (
    <footer className="py-6 px-4 mt-auto bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
      <div className="max-w-2xl mx-auto">
        <p className="text-sm text-center text-gray-600 dark:text-gray-400">
          © {' '}
          <a
            href="#"
            className="text-inherit hover:text-primary-main hover:underline transition-colors"
          >
            Mountain Stream Tracker
          </a>{' '}
          {new Date().getFullYear()}
        </p>
      </div>
    </footer>
  );
}