const Footer = () => (
  <footer className="text-white body-font bg-zinc-600">
    <div className="container px-5 py-8 mx-auto flex flex-col sm:flex-row items-center">
      {/* Footer 텍스트 */}
      <div className="text-center sm:text-left sm:ml-1 flex flex-col">
        <span className="font-custom text-lg">고려대학교 SW 지능정보 아카데미 2조</span>
        <span className="font-second text-sm mt-2 font-medium">
          안지홍, 유지혜, 이승재, 이정현, 하동우, 홍규린</span>
        <span className="font-second text-sm font-medium text-black">
        © 2024 Lumterior. All rights reserved.</span>
      </div>

      {/* git 아이콘 */}
      <span className="inline-flex mt-4 sm:mt-0 sm:ml-auto justify-center flex-wrap">
        <a
          href="https://github.com/jihyeyoo/inisw.git"
          className="text-gray-600"
          target="_blank"
          rel="noopener noreferrer"
        >
          <svg
            fill="white"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            className="w-8 h-8 sm:w-7 sm:h-7 md:w-8 md:h-8 ml-5 relative top-[-3px]"
            viewBox="0 0 16 16"
          >
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
          </svg>
        </a>
      </span>
    </div>
  </footer>
);

export default Footer;
