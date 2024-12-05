import Link from "next/link";

interface NavbarProps {
    backgroundColor: string; // 'rgb(255, 0, 0)' 형태의 문자열을 받음
}

const Navbar = ({ backgroundColor }: NavbarProps) => {
    return (
        <nav
            className="p-4"
            style={{
                backgroundColor, // TailwindCSS로 동적 배경색 처리 불가능, 인라인 스타일 사용
            }}
        >
            <Link href="/">
                LumTerior
            </Link>
        </nav>
    );
}

export default Navbar;