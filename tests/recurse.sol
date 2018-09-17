contract C{
    
    function f0(){

    }

    function f1(){
        f0();
    }

    function f2(){
        f0();
        f1();
    }

    function (){
        f2();
    }
}
