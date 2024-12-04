import React from 'react';
import Link from 'next/link';

interface NavbarProps {
  backgroundColor: string; // 'rgb(255, 0, 0)' 형태의 문자열을 받음
}

const Navbar: React.FC<NavbarProps> = ({ backgroundColor }) => {
  return (
    <nav style={{ backgroundColor, padding: '1rem' }}>
      <Link href="/" passHref>
      <div className="navbar-title">
        LumTerior
      </div>
      </Link>
    </nav>
  );
}

export default Navbar;